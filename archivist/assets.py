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
          "https://app.rkvst.io",
          authtoken,
      )
      asset = arch.assets.create(...)

"""

from logging import getLogger
from typing import Dict, Optional, Tuple
from copy import deepcopy

# pylint:disable=unused-import      # To prevent cyclical import errors forward referencing is used
# pylint:disable=cyclic-import      # but pylint doesn't understand this feature
from . import archivist as type_helper


from .constants import (
    ASSETS_SUBPATH,
    ASSETS_LABEL,
    CONFIRMATION_STATUS,
)
from . import confirmer
from .dictmerge import _deepmerge
from .errors import ArchivistNotFoundError
from .type_aliases import NoneOnError
from .utils import selector_signature

# These are now hardcoded and not user-selectable. Eventually they will be removed from
# the backend API and removed from this package.
BEHAVIOURS = [
    "Attachments",
    "RecordEvidence",
]

LOGGER = getLogger(__name__)


class Asset(dict):
    """Asset

    Asset object has dictionary attributes and properties.

    """

    @property
    def primary_image(self) -> NoneOnError[str]:
        """Primary Image

        Attachment that is the primary image of the asset.

        Returns:
            :class:`Attachment` instance

        """
        try:
            attachments = self["attributes"]["arc_attachments"]
        except (KeyError, TypeError):
            pass
        else:
            return next(  # pragma: no cover
                (
                    a
                    for a in attachments
                    if "arc_display_name" in a
                    if a["arc_display_name"] == "arc_primary_image"
                ),
                None,
            )

        return None

    @property
    def name(self) -> NoneOnError[str]:
        """str: name of the asset"""
        name = None
        try:
            name = self["attributes"]["arc_display_name"]
        except (KeyError, TypeError):
            pass

        return name


class _AssetsClient:
    """AssetsClient

    Access to assets entities using CRUD interface. This class is usually
    accessed as an attribute of the Archivist class.

    Args:
        archivist (Archivist): :class:`Archivist` instance

    """

    def __init__(self, archivist: "type_helper.Archivist"):
        self._archivist = archivist

    def __str__(self) -> str:
        return f"AssetsClient({self._archivist.url})"

    def create(
        self,
        *,
        props: Optional[Dict] = None,
        attrs: Optional[Dict] = None,
        confirm: bool = False,
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
        newprops = _deepmerge({"behaviours": BEHAVIOURS}, props)
        data = self.__params(newprops, attrs)
        return self.create_from_data(data, confirm=confirm)

    def create_from_data(self, data: Dict, *, confirm: bool = False) -> Asset:
        """Create asset

        Creates asset with request body from data stream.
        Suitable for reading data from a file using json.load or yaml.load

        Args:
            data (dict): request body of asset.
            confirm (bool): if True wait for asset to be confirmed on DLT.

        Returns:
            :class:`Asset` instance

        """
        asset = Asset(
            **self._archivist.post(
                f"{ASSETS_SUBPATH}/{ASSETS_LABEL}",
                data,
            )
        )
        if not confirm:
            return asset

        return self.wait_for_confirmation(asset["identity"])

    def create_if_not_exists(
        self, data: Dict, *, confirm: bool = False
    ) -> Tuple[Asset, bool]:
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
                  - Attachments
                attributes:
                  arc_display_name: Jitsuin Front Door
                  arc_firmware_version: "1.0"
                  arc_serial_number: das-j1-01
                  arc_description: Electronic door entry system to Jitsuin France
                  wavestone_asset_id: paris.france.jitsuin.das
                location:
                  selector:
                    - display_name
                  display_name: Jitsuin Paris,
                  description: Sales and sales support for the French region
                  latitude: 48.8339211,
                  longitude: 2.371345,
                  attributes:
                    address: 5 Parvis Alan Turing, 75013 Paris, France
                    wavestone_ext: managed
                attachments:
                  - filename: functests/test_resources/doors/assets/entry-terminal.jpg
                    content_type: image/jpg

            The 'selector' value is required and will usually specify the 'arc_display_name' as a
            secondary key. The keys in 'selector' must exist in the attributes of the asset.

            If 'location' is specified then the 'selector' value is required and is used as a
            secondary key. Likewise the secondary key must exist in the attributes of the location.

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
            loc, _ = self._archivist.locations.create_if_not_exists(
                location,
            )
            data["attributes"]["arc_home_location_identity"] = loc["identity"]

        # any attachments ?
        if attachments is not None:
            data["attributes"]["arc_attachments"] = [
                self._archivist.attachments.create(a) for a in attachments
            ]

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

    def read(self, identity: str) -> Asset:
        """Read asset

        Reads asset.

        Args:
            identity (str): assets identity e.g. assets/xxxxxxxxxxxxxxxxxxxxxxx

        Returns:
            :class:`Asset` instance

        """
        return Asset(**self._archivist.get(ASSETS_SUBPATH, identity))

    def __params(self, props: Optional[Dict], attrs: Optional[Dict]) -> Dict:
        params = deepcopy(props) if props else {}
        if attrs:
            params["attributes"] = attrs

        return _deepmerge(self._archivist.fixtures.get(ASSETS_LABEL), params)

    def count(
        self, *, props: Optional[Dict] = None, attrs: Optional[Dict] = None
    ) -> int:
        """Count assets.

        Counts number of assets that match criteria.

        Args:
            props (dict): e.g. {"confirmation_status": "CONFIRMED" }
            attrs (dict): e.g. {"arc_display_type": "door" }

        Returns:
            integer count of assets.

        """
        return self._archivist.count(
            f"{ASSETS_SUBPATH}/{ASSETS_LABEL}", params=self.__params(props, attrs)
        )

    def wait_for_confirmed(
        self, *, props: Optional[Dict] = None, attrs: Optional[Dict] = None
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

    def list(
        self,
        *,
        page_size: Optional[int] = None,
        props: Optional[Dict] = None,
        attrs: Optional[Dict] = None,
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
                f"{ASSETS_SUBPATH}/{ASSETS_LABEL}",
                ASSETS_LABEL,
                page_size=page_size,
                params=self.__params(props, attrs),
            )
        )

    def read_by_signature(
        self, *, props: Optional[Dict] = None, attrs: Optional[Dict] = None
    ) -> Asset:
        """Read Asset by signature.

        Reads asset that meets criteria. Only one asset is expected.

        Args:
            props (dict): e.g. {"tracked": "TRACKED" }
            attrs (dict): e.g. {"arc_display_type": "door" }

        Returns:
            :class:`Asset` instance

        """
        return Asset(
            **self._archivist.get_by_signature(
                f"{ASSETS_SUBPATH}/{ASSETS_LABEL}",
                ASSETS_LABEL,
                params=self.__params(props, attrs),
            )
        )
