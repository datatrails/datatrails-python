"""Assets interface

   Access to the assets endpoint.

   The user is not expected to use this class directly. It is an attribute of the
   :class:`Archivist` class.

   For example instantiate an Archivist instance and execute the methods of the class:

   .. code-block:: python

      with open(".auth_token", mode="r") as tokenfile:
          authtoken = tokenfile.read().strip()

      # Initialize connection to Archivist
      arch = Archivist(
          "https://app.rkvst.io",
          auth=authtoken,
      )
      asset = arch.assets.create(...)

"""

import logging
from typing import Dict, Optional
from copy import deepcopy

from archivist.type_aliases import NoneOnError

# pylint:disable=unused-import      # To prevent cyclical import errors forward referencing is used
# pylint:disable=cyclic-import      # but pylint doesn't understand this feature
from archivist import archivist as type_helper


from .constants import (
    ASSETS_SUBPATH,
    ASSETS_LABEL,
    CONFIRMATION_STATUS,
)
from . import confirmer
from .dictmerge import _deepmerge
from .errors import ArchivistNotFoundError

#: Default page size - number of entities fetched in one REST GET in the
#: :func:`~_AssetsClient.list` method. This can be overridden but should rarely
#: be changed.
DEFAULT_PAGE_SIZE = 500

# These are now hardcoded and not user-selectable. Eventually they will be removed from
# the backend API and removed from this package.
BEHAVIOURS = [
    "Attachments",
    "RecordEvidence",
]

LOGGER = logging.getLogger(__name__)


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
        try:
            name = self["attributes"]["arc_display_name"]
        except (KeyError, TypeError):
            pass
        else:
            return name

        return None


FIXTURE_LABEL = "assets"


class _AssetsClient:
    """AssetsClient

    Access to assets entities using CRUD interface. This class is usually
    accessed as an attribute of the Archivist class.

    Args:
        archivist (Archivist): :class:`Archivist` instance

    """

    def __init__(self, archivist: "type_helper.Archivist"):
        self._archivist = archivist

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
            props (dict): Properties - usually only the storage_integrity setting
            attrs (dict): attributes of created asset.
            confirm (bool): if True wait for asset to be confirmed.

        Returns:
            :class:`Asset` instance

        """
        LOGGER.debug("Create Asset %s", attrs)
        data = self.__query(props, attrs)
        data["behaviours"] = BEHAVIOURS
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

    def wait_for_confirmation(self, identity: str) -> bool:
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

    def __query(self, props: Optional[Dict], attrs: Optional[Dict]) -> Dict:
        query = deepcopy(props) if props else {}
        if attrs:
            query["attributes"] = attrs

        return _deepmerge(self._archivist.fixtures.get(FIXTURE_LABEL), query)

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
            f"{ASSETS_SUBPATH}/{ASSETS_LABEL}", query=self.__query(props, attrs)
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
        page_size: int = DEFAULT_PAGE_SIZE,
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
                query=self.__query(props, attrs),
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
                query=self.__query(props, attrs),
            )
        )
