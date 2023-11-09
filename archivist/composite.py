"""Composite interface

   Access to various utility methods that access various endpoints.

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
      asset = arch.composite.......(...)

"""


from logging import getLogger
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # pylint:disable=cyclic-import      # but pylint doesn't understand this feature
    from .archivist import Archivist


LOGGER = getLogger(__name__)


class _CompositeClient:
    """CompositeClient

    Access to various composite methods,
    accessed as an attribute of the Archivist class.

    Args:
        archivist (Archivist): :class:`Archivist` instance

    These mthods are not unittested and provided as a convenience.
    """

    def __init__(self, archivist_instance: "Archivist"):
        self._archivist = archivist_instance

    def __str__(self) -> str:
        return f"CompositeClient({self._archivist.url})"

    def estate_info(self):
        """
        Evaluate health of the various assets and events in the system

        The report is emitted using LOGGER.info statements
        """
        num_events = self._archivist.events.count()
        num_assets = self._archivist.assets.count()
        num_locations = self._archivist.locations.count()

        LOGGER.info(
            (
                "There are %s events registered against %s assets"
                " in the system spread over %s locations."
            ),
            num_events,
            num_assets,
            num_locations,
        )
