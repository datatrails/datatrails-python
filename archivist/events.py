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
          "https://rkvst.poc.jitsuin.io",
          auth=authtoken,
      )
      asset = arch.assets.create(...)
      event = arch.events.create(asset['identity'], ...)

"""

from copy import deepcopy

from .constants import (
    SEP,
    ASSETS_SUBPATH,
    ASSETS_WILDCARD,
    EVENTS_LABEL,
)
from .confirm import wait_for_confirmation, wait_for_confirmed


#: Default page size - number of entities fetched in one call to the
#: :func:`~_EventsClient.list` method.
DEFAULT_PAGE_SIZE = 500


class _EventsClient:
    """EventsClient

    Access to events entities using the CRUD interface. This class is usually
    accessed as an attribute of the Archivist class.

    Args:
        archivist (Archivist): :class:`Archivist` instance

    """

    def __init__(self, archivist):
        self._archivist = archivist

    def create(self, asset_id, props, attrs, *, asset_attrs=None, confirm=False):
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

        return self.create_from_data(
            asset_id,
            self.__query(props, attrs, asset_attrs),
            confirm=confirm,
        )

    def create_from_data(self, asset_id, data, *, confirm=False):
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

        return wait_for_confirmation(self, event["identity"])

    def read(self, identity):
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

    @staticmethod
    def __query(props, attrs, asset_attrs):
        query = deepcopy(props) if props else {}
        if attrs:
            query["event_attributes"] = attrs
        if asset_attrs:
            query["asset_attributes"] = asset_attrs

        return query

    def count(
        self, *, asset_id=ASSETS_WILDCARD, props=None, attrs=None, asset_attrs=None
    ):
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
        self, *, asset_id=ASSETS_WILDCARD, props=None, attrs=None, asset_attrs=None
    ):
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
        return wait_for_confirmed(
            self, asset_id=asset_id, props=props, attrs=attrs, asset_attrs=asset_attrs
        )

    def list(
        self,
        *,
        asset_id=ASSETS_WILDCARD,
        page_size=DEFAULT_PAGE_SIZE,
        props=None,
        attrs=None,
        asset_attrs=None,
    ):
        """List events.

        Lists events that match criteria.

        Args:
            asset_id (str): optional asset identity e.g. assets/xxxxxxxxxxxxxxxxxxxxxxxxxx
            props (dict): e.g. {"tracked": "TRACKED" }
            attrs (dict): e.g. {"arc_display_type": "open" }
            asset_attrs (dict): optional asset_attributes e.g. {"arc_display_type": "door" }
            page_sixe (int): optional page size. (Rarely used).

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
        asset_id=ASSETS_WILDCARD,
        props=None,
        attrs=None,
        asset_attrs=None,
    ):
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
