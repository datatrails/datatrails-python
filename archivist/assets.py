"""Assets interface

   Access to the assets endpoint.

   The user is not expected to use this class directly. It is an attribute of the
   :class:`Archivist` class.

   For example instantiate an Archivist instance and execute the methods of the class:

   .. code-block:: python

      with open(".auth_token", mode="r", encoding="utf-8") as tokenfile:
          authtoken = tokenfile.read().strip()

      # Initialize connection to Archivist
      arch = Archivist(
          "https://app.datatrails.ai",
          authtoken,
      )
      asset = arch.assets.create(...)

"""


from copy import deepcopy
from logging import getLogger
from typing import TYPE_CHECKING, Any

# pylint:disable=cyclic-import      # but pylint doesn't understand this feature
from . import confirmer
from .asset import Asset
from .constants import (
    ASSET_BEHAVIOURS,
    ASSETS_LABEL,
    ASSETS_SUBPATH,
    CONFIRMATION_STATUS,
)
from .dictmerge import _deepmerge
from .errors import ArchivistBadFieldError, ArchivistNotFoundError
from .utils import selector_signature

if TYPE_CHECKING:
    from .archivist import Archivist

LOGGER = getLogger(__name__)


class _AssetsPublic:
    """AssetsReader

    Access to assets entities using CRUD interface. This class is usually
    accessed as an attribute of the Archivist or Public class.

    Args:
        archivist (Archivist): :class:`Archivist` instance

    """

    def __init__(self, archivist_instance: "Archivist"):
        self._archivist = archivist_instance
        self._public = archivist_instance.public
        self._subpath = f"{archivist_instance.root}/{ASSETS_SUBPATH}"

    def __str__(self) -> str:
        return "AssetsPublic()"

    def _identity(self, identity: str) -> str:
        """Return fully qualified identity
        If public then expect a full url as argument
        """
        if self._public:
            return identity

        return f"{self._subpath}/{identity}"

    def read(self, identity: str) -> Asset:
        """Read asset

        Reads asset.

        Args:
            identity (str): assets identity e.g. assets/xxxxxxxxxxxxxxxxxxxxxxx

        Returns:
            :class:`Asset` instance

        """
        return Asset(**self._archivist.get(self._identity(identity)))


class _AssetsRestricted(_AssetsPublic):
    """AssetsRestricted

    Access to assets entities using CRUD interface. This class is usually
    accessed as an attribute of the Archivist or Public class.

    Args:
        archivist (Archivist): :class:`Archivist` instance

    """

    def __init__(self, archivist_instance: "Archivist"):
        super().__init__(archivist_instance)
        self._label = f"{self._subpath}/{ASSETS_LABEL}"
        self.pending_count: int = 0

    def __str__(self) -> str:
        return f"AssetsRestricted({self._archivist.url})"

    def __params(
        self, props: "dict[str, Any]|None", attrs: "dict[str, Any]|None"
    ) -> "dict[str, Any]":
        params = deepcopy(props) if props else {}
        if attrs:
            params["attributes"] = attrs

        return _deepmerge(self._archivist.fixtures.get(f"{ASSETS_LABEL}"), params)

    def create(
        self,
        *,
        props: "dict[str, Any]|None" = None,
        attrs: "dict[str, Any]|None" = None,
        confirm: bool = True,
    ) -> Asset:
        """Create asset

        Creates asset with defined properties and attributes.

        Args:
            props (dict): Properties - usually only the proof_mechanism setting
            attrs (dict): attributes of created asset.
            confirm (bool): if True wait for asset to be confirmed.

        Returns:
            :class:`Asset` instance

        """
        LOGGER.debug("Create Asset %s", attrs)
        # default behaviours  are added first - any set in user-specified fixtures or
        # in the method args will overide...
        newprops = _deepmerge({"behaviours": ASSET_BEHAVIOURS}, props)
        data = self.__params(newprops, attrs)
        return self.create_from_data(data, confirm=confirm)

    def create_from_data(
        self, data: "dict[str, Any]", *, confirm: bool = True
    ) -> Asset:
        """Create asset

        Creates asset with request body from data stream.
        Suitable for reading data from a file using json.load or yaml.load

        Args:
            data (dict): request body of asset.
            confirm (bool): if True wait for asset to be confirmed on DLT.

        Returns:
            :class:`Asset` instance

        """
        asset = Asset(**self._archivist.post(self._label, data))
        if not confirm:
            return asset

        return self.wait_for_confirmation(asset["identity"])

    def create_if_not_exists(
        self, data: "dict[str, Any]", *, confirm: bool = True
    ) -> "tuple[Asset, bool]":
        """
        Creates an asset and associated locations and attachments if asset
        does not already exist.

        Args:
            data (dict): request body of asset.
            confirm (bool): if True wait for asset to be confirmed on DLT.

        A YAML representation of the data argument would be:

            .. code-block:: yaml

                selector:
                  - attributes:
                    - arc_display_name
                behaviours
                  - RecordEvidence
                attributes:
                  arc_display_name: DATATRAILS Front Door
                  arc_firmware_version: "1.0"
                  arc_serial_number: das-j1-01
                  arc_description: Electronic door entry system to DATATRAILS France
                  wavestone_asset_id: paris.france.datatrails.das
                location:
                  identity: locations/xxxxxxxxxxxxxxxxxxxxxxxxxx
                location:
                  selector:
                    - display_name
                  display_name: DATATRAILS Paris
                  description: Sales and sales support for the French region
                  latitude: 48.8339211,
                  longitude: 2.371345,
                  attributes:
                    address: 5 Parvis Alan Turing, 75013 Paris, France
                    wavestone_ext: managed
                attachments:
                  - filename: functests/test_resources/doors/assets/entry-terminal.jpg
                    content_type: image/jpg
                    attachment: terminal entry

            The 'selector' value is required and will usually specify the 'arc_display_name' as a
            secondary key. The keys in 'selector' must exist in the attributes of the asset.

            If 'location' is specified then the 'selector' value is required and is used as a
            secondary key. Likewise the secondary key must exist in the attributes of the location.

            Alternatively the identity of the location is specified - both
            are shown - choose one.

        Returns:
            tuple of :class:`Asset` instance, Boolean is True if asset already existed

        """

        asset = None
        existed = False
        data = deepcopy(data)
        attachments = data.pop("attachments", None)
        location = data.pop("location", None)
        selector = data.pop("selector")  # must exist
        props, attrs = selector_signature(selector, data)
        try:
            asset = self.read_by_signature(props=props, attrs=attrs)

        except ArchivistNotFoundError:
            LOGGER.info(
                "asset with selector %s,%s does not exist - creating", props, attrs
            )

        else:
            LOGGER.info("asset with selector %s,%s already exists", props, attrs)
            return asset, True

        # is location present?
        if location is not None:
            if "identity" in location:
                data["attributes"]["arc_home_location_identity"] = location["identity"]
            else:
                loc, _ = self._archivist.locations.create_if_not_exists(
                    location,
                )
                data["attributes"]["arc_home_location_identity"] = loc["identity"]

        # any attachments ?
        if attachments is not None:
            for a in attachments:
                # attempt to get attachment to use as a key
                attachment_key = a.get("attachment", None)
                if attachment_key is None:
                    # failing that create a key from filename or url
                    attachment_key = self._archivist.attachments.get_default_key(a)
                data["attributes"][attachment_key] = self._archivist.attachments.create(
                    a
                )

        asset = self.create_from_data(
            data=data,
            confirm=confirm,
        )

        return asset, existed

    def wait_for_confirmation(self, identity: str) -> Asset:
        """Wait for asset to be confirmed.

        Waits asset to be confirmed.

        Args:
            identity (str): identity of asset

        Returns:
            True if asset is confirmed.

        """
        confirmer.MAX_TIME = self._archivist.max_time
        # pylint: disable=protected-access
        return confirmer._wait_for_confirmation(self, identity)

    def wait_for_confirmed(
        self,
        *,
        props: "dict[str, Any]|None" = None,
        attrs: "dict[str, Any]|None" = None,
    ) -> bool:
        """Wait for assets to be confirmed.

        Waits for all assets that match criteria to be confirmed.

        Args:
            props (dict): e.g. {"tracked": "TRACKED" }
            attrs (dict): e.g. {"arc_display_type": "door" }

        Returns:
            True if all assets are confirmed.

        """
        # check that entities exist
        newprops = deepcopy(props) if props else {}
        newprops.pop(CONFIRMATION_STATUS, None)

        LOGGER.debug("Count assets %s", newprops)
        count = self.count(props=newprops, attrs=attrs)
        if count == 0:
            raise ArchivistNotFoundError("No assets exist")

        confirmer.MAX_TIME = self._archivist.max_time
        # pylint: disable=protected-access
        return confirmer._wait_for_confirmed(self, props=newprops, attrs=attrs)

    def count(
        self,
        *,
        props: "dict[str, Any]|None" = None,
        attrs: "dict[str, Any]|None" = None,
    ) -> int:
        """Count assets.

        Counts number of assets that match criteria.

        Args:
            props (dict): e.g. {"confirmation_status": "CONFIRMED" }
            attrs (dict): e.g. {"arc_display_type": "door" }

        Returns:
            integer count of assets.

        """
        return self._archivist.count(self._label, params=self.__params(props, attrs))

    def list(
        self,
        *,
        page_size: "int|None" = None,
        props: "dict[str, Any]|None" = None,
        attrs: "dict[str, Any]|None" = None,
    ):
        """List assets.

        Lists assets that match criteria.

        Args:
            props (dict): optional e.g. {"tracked": "TRACKED" }
            attrs (dict): optional e.g. {"arc_display_type": "door" }
            page_size (int): optional page size. (Rarely used).

        Returns:
            iterable that returns :class:`Asset` instances

        """
        return (
            Asset(**a)
            for a in self._archivist.list(
                self._label,
                ASSETS_LABEL,
                page_size=page_size,
                params=self.__params(props, attrs),
            )
        )

    def read_by_signature(
        self,
        *,
        props: "dict[str, Any]|None" = None,
        attrs: "dict[str, Any]|None" = None,
    ) -> Asset:
        """Read Asset by signature.

        Reads asset that meets criteria. Only one asset is expected.

        Args:
            props (dict): e.g. {"tracked": "TRACKED" }
            attrs (dict): e.g. {"arc_display_type": "door" }

        Returns:
            :class:`Asset` instance

        """
        assets_label = f"public{ASSETS_LABEL}" if self._public else ASSETS_LABEL
        return Asset(
            **self._archivist.get_by_signature(
                self._label,
                assets_label,
                params=self.__params(props, attrs),
            )
        )

    def publicurl(self, identity: str) -> str:
        """Read asset public url

        Reads assets public url.

        Args:
            identity (str): assets identity e.g. assets/xxxxxxxxxxxxxxxxxxxxxxx

        Returns:
            :str: publicurl as string

        """
        body = self._archivist.get(f"{self._identity(identity)}:publicurl")
        publicurl = body.get("publicurl")
        if publicurl is None:
            raise ArchivistBadFieldError("No publicurl found in response")

        return publicurl
