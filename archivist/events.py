"""Events interface

   Direct access to the events endpoint.

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
      event = arch.events.create(asset['identity'], ...)

"""

import logging
from typing import Dict, Optional
from copy import deepcopy

# pylint:disable=unused-import      # To prevent cyclical import errors forward referencing is used
# pylint:disable=cyclic-import      # but pylint doesn't understand this feature
from archivist import archivist as type_helper

from .constants import (
    SEP,
    ASSETS_SUBPATH,
    ASSETS_WILDCARD,
    CONFIRMATION_STATUS,
    EVENTS_LABEL,
)
from . import confirmer
from .dictmerge import _deepmerge
from .errors import ArchivistNotFoundError


#: Default page size - number of entities fetched in one REST GET in the
#: :func:`~_EventsClient.list` method. This can be overridden but should rarely
#: be changed.
DEFAULT_PAGE_SIZE = 500

FIXTURE_LABEL = "events"

LOGGER = logging.getLogger(__name__)


class Event(dict):
    """Event

    Event object has dictionary attributes and properties.

    """

    @property
    def when(self):
        """when

        Timestamp of event

        """
        try:
            when = self["timestamp_declared"]
        except KeyError:
            pass
        else:
            return when

        try:
            when = self["timestamp_accepted"]
        except KeyError:
            pass
        else:
            return when

        return None

    @property
    def who(self):
        """who

        Principal identity.

        """

        try:
            who = self["principal_declared"]["display_name"]
        except (KeyError, TypeError):
            pass
        else:
            return who

        try:
            who = self["principal_accepted"]["display_name"]
        except (KeyError, TypeError):
            pass
        else:
            return who

        return None


class _EventsClient:
    """EventsClient

    Access to events entities using the CRUD interface. This class is usually
    accessed as an attribute of the Archivist class.

    Args:
        archivist (Archivist): :class:`Archivist` instance

    """

    def __init__(self, archivist: "type_helper.Archivist"):
        self._archivist = archivist

    def create(
        self,
        asset_id: str,
        props: Dict,
        attrs: Dict,
        *,
        asset_attrs: Optional[Dict] = None,
        confirm: bool = False,
    ) -> Event:
        """Create event

        Creates event for given asset.

        Args:
            asset_id (str): asset identity e.g. assets/xxxxxxxxxxxxxxxxxxxxxxxxxx
            props (dict): properties for this event.
            attrs (dict): attributes of created event.
            asset_attrs (dict): attributes of referenced asset.
            confirm (bool): if True wait for event to be confirmed on DLT.

        Returns:
            :class:`Event` instance

        """

        LOGGER.debug("Create Event %s/%s", asset_id, props)
        return self.create_from_data(
            asset_id,
            self.__query(props, attrs, asset_attrs),
            confirm=confirm,
        )

    def create_from_data(self, asset_id: str, data: Dict, *, confirm=False) -> Event:
        """Create event

        Creates event for given asset from data.
        Suitable for reading data from json.load or yaml.load from a file

        Args:
            asset_id (str): asset identity e.g. assets/xxxxxxxxxxxxxxxxxxxxxxxxxx
            attrs (dict): request body of event.
            confirm (bool): if True wait for event to be confirmed on DLT.

        Returns:
            :class:`Event` instance

        """
        event = Event(
            **self._archivist.post(
                SEP.join((ASSETS_SUBPATH, asset_id, EVENTS_LABEL)),
                data,
            )
        )
        if not confirm:
            return event

        return self.wait_for_confirmation(event["identity"])

    def wait_for_confirmation(self, identity: str) -> bool:
        """Wait for event to be confirmed.

        Waits for event to be confirmed.

        Args:
            identity (str): identity of event

        Returns:
            True if event is confirmed.

        """
        confirmer.MAX_TIME = self._archivist.max_time
        # pylint: disable=protected-access
        return confirmer._wait_for_confirmation(self, identity)

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
                ASSETS_SUBPATH,
                identity,
            )
        )

    def __query(
        self, props: Optional[Dict], attrs: Optional[Dict], asset_attrs: Optional[Dict]
    ) -> Dict:
        query = deepcopy(props) if props else {}
        if attrs:
            query["event_attributes"] = attrs
        if asset_attrs:
            query["asset_attributes"] = asset_attrs

        return _deepmerge(self._archivist.fixtures.get(FIXTURE_LABEL), query)

    def count(
        self,
        *,
        asset_id: str = ASSETS_WILDCARD,
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
            SEP.join((ASSETS_SUBPATH, asset_id, EVENTS_LABEL)),
            query=self.__query(props, attrs, asset_attrs),
        )

    def wait_for_confirmed(
        self,
        *,
        asset_id: str = ASSETS_WILDCARD,
        props: Optional[Dict] = None,
        attrs: Optional[Dict] = None,
        asset_attrs: Optional[Dict] = None,
    ) -> bool:
        """Wait for events to be confirmed.

        Waits for all events that match criteria to be confirmed.

        Args:
            asset_id (str): optional asset identity e.g. assets/xxxxxxxxxxxxxxxxxxxxxxxxxx
            props (dict): e.g. {"tracked": "TRACKED" }
            attrs (dict): e.g. {"arc_display_type": "open" }
            asset_attrs (dict): optional asset_attributes e.g. {"arc_display_type": "door" }

        Returns:
            True if all events are confirmed.

        """
        # check that entities exist
        newprops = deepcopy(props) if props else {}
        newprops.pop(CONFIRMATION_STATUS, None)

        LOGGER.debug("Count events %s", newprops)
        count = self.count(
            asset_id=asset_id, props=newprops, attrs=attrs, asset_attrs=asset_attrs
        )
        if count == 0:
            raise ArchivistNotFoundError("No events exist")

        confirmer.MAX_TIME = self._archivist.max_time
        # pylint: disable=protected-access
        return confirmer._wait_for_confirmed(
            self, asset_id=asset_id, props=props, attrs=attrs, asset_attrs=asset_attrs
        )

    def list(
        self,
        *,
        asset_id: str = ASSETS_WILDCARD,
        page_size: int = DEFAULT_PAGE_SIZE,
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
                SEP.join((ASSETS_SUBPATH, asset_id, EVENTS_LABEL)),
                EVENTS_LABEL,
                page_size=page_size,
                query=self.__query(props, attrs, asset_attrs),
            )
        )

    def read_by_signature(
        self,
        *,
        asset_id: str = ASSETS_WILDCARD,
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
                SEP.join((ASSETS_SUBPATH, asset_id, EVENTS_LABEL)),
                EVENTS_LABEL,
                query=self.__query(props, attrs, asset_attrs),
            )
        )
