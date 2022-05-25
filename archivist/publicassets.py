"""Assets interface

   Access to the publicassets endpoint.

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
      asset = arch.publicassets.get(...)

"""

from logging import getLogger

# pylint:disable=unused-import      # To prevent cyclical import errors forward referencing is used
# pylint:disable=cyclic-import      # but pylint doesn't understand this feature
from . import archivist as type_helper


from .assets import Asset
from .constants import (
    PUBLICASSETS_SUBPATH,
    PUBLICASSETS_LABEL,
)
from .dictmerge import _deepmerge

LOGGER = getLogger(__name__)


class _PublicAssetsClient:
    """PublicAssetsClient

    Access to publicassets entities using CRUD interface. This class is usually
    accessed as an attribute of the Archivist class.

    Args:
        archivist (Archivist): :class:`Archivist` instance

    """

    def __init__(self, archivist: "type_helper.Archivist"):
        self._archivist = archivist

    def __str__(self) -> str:
        return f"PublicAssetsClient({self._archivist.url})"

    def read(self, identity: str) -> Asset:
        """Read publicasset

        Reads publicasset.

        Args:
            identity (str): assets identity e.g. assets/xxxxxxxxxxxxxxxxxxxxxxx

        Returns:
            :class:`Asset` instance

        """
        return Asset(**self._archivist.get(PUBLICASSETS_SUBPATH, identity))
