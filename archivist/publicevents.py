"""PublicEvents interface

   Direct access to the events endpoint.

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
      asset = arch.assets.create(...public=True)
      event = arch.publicevents.list(asset['identity'], ...)

"""

from copy import deepcopy
from logging import getLogger
from typing import Dict, Optional

# pylint:disable=unused-import      # To prevent cyclical import errors forward referencing is used
# pylint:disable=cyclic-import      # but pylint doesn't understand this feature
from . import archivist as type_helper

from .constants import (
    EVENTS_LABEL,
    SEP,
    PUBLICASSETS_SUBPATH,
)
from .dictmerge import _deepmerge
from .events import Event


LOGGER = getLogger(__name__)


class _PublicEventsClient:
    """PublicEventsClient

    Access to events entities using the CRUD interface. This class is usually
    accessed as an attribute of the Archivist class.

    Args:
        archivist (Archivist): :class:`Archivist` instance

    """

    PREFIX = "public"

    def __init__(self, archivist: "type_helper.Archivist"):
        self._archivist = archivist

    def __str__(self) -> str:
        return f"PublicEventsClient({self._archivist.url})"

    def __prefix(self, asset_id: str):
        """Prefixes identity"""
        if asset_id.startswith(self.PREFIX):
            return asset_id

        return f"{self.PREFIX}{asset_id}"

    def read(self, identity: str) -> Event:
        """Read event

        Reads event.

        Args:
            identity (str): events identity e.g. assets/xxxxxxx.../events/yyyyyyy...

        Returns:
            :class:`Event` instance

        """
        return Event(
            **self._archivist.get(
                PUBLICASSETS_SUBPATH,
                self.__prefix(identity),
            )
        )

    def __params(
        self, props: Optional[Dict], attrs: Optional[Dict], asset_attrs: Optional[Dict]
    ) -> Dict:
        params = deepcopy(props) if props else {}
        if attrs:
            params["event_attributes"] = attrs
        if asset_attrs:
            params["asset_attributes"] = asset_attrs

        return _deepmerge(self._archivist.fixtures.get(EVENTS_LABEL), params)

    def count(
        self,
        *,
        asset_id: Optional[str] = None,
        props: Optional[Dict] = None,
        attrs: Optional[Dict] = None,
        asset_attrs: Optional[Dict] = None,
    ) -> int:
        """Count events.

        Counts number of events that match criteria.

        Args:
            asset_id (str): optional asset identity e.g. assets/xxxxxxxxxxxxxxxxxxxxxxxxxx
            props (dict): optional properties e.g. {"confirmation_status": "CONFIRMED" }
            attrs (dict): optional attributes e.g. {"arc_display_type": "open" }
            asset_attrs (dict): optional asset_attributes e.g. {"arc_display_type": "door" }

        Returns:
            integer count of assets.

        """

        return self._archivist.count(
            SEP.join((PUBLICASSETS_SUBPATH, self.__prefix(asset_id), EVENTS_LABEL)),
            params=self.__params(props, attrs, asset_attrs),
        )

    def list(
        self,
        *,
        asset_id: Optional[str] = None,
        page_size: Optional[int] = None,
        props: Optional[Dict] = None,
        attrs: Optional[Dict] = None,
        asset_attrs: Optional[Dict] = None,
    ):
        """List events.

        Lists events that match criteria.

        Args:
            asset_id (str): optional asset identity e.g. assets/xxxxxxxxxxxxxxxxxxxxxxxxxx
            props (dict): e.g. {"tracked": "TRACKED" }
            attrs (dict): e.g. {"arc_display_type": "open" }
            asset_attrs (dict): optional asset_attributes e.g. {"arc_display_type": "door" }
            page_size (int): optional page size. (Rarely used).

        Returns:
            iterable that returns :class:`Event` instances

        """
        return (
            Event(**a)
            for a in self._archivist.list(
                SEP.join((PUBLICASSETS_SUBPATH, self.__prefix(asset_id), EVENTS_LABEL)),
                EVENTS_LABEL,
                page_size=page_size,
                params=self.__params(props, attrs, asset_attrs),
            )
        )

    def read_by_signature(
        self,
        *,
        asset_id: Optional[str] = None,
        props: Optional[Dict] = None,
        attrs: Optional[Dict] = None,
        asset_attrs: Optional[Dict] = None,
    ) -> Event:
        """Read event by signature.

        Reads event that meets criteria. Only one event is expected.

        Args:
            asset_id (str): optional asset identity e.g. assets/xxxxxxxxxxxxxxxxxxxxxxxxxx
            props (dict): e.g. {"tracked": "TRACKED" }
            attrs (dict): e.g. {"arc_display_type": "open" }
            asset_attrs (dict): optional asset_attributes e.g. {"arc_display_type": "door" }

        Returns:
            :class:`Event` instance

        """
        return Event(
            **self._archivist.get_by_signature(
                SEP.join((PUBLICASSETS_SUBPATH, self.__prefix(asset_id), EVENTS_LABEL)),
                EVENTS_LABEL,
                params=self.__params(props, attrs, asset_attrs),
            )
        )
