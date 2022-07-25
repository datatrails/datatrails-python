"""Events interface

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
      asset = arch.assets.create(...)
      event = arch.events.create(asset['identity'], ...)

"""

from __future__ import annotations
from copy import deepcopy
from logging import getLogger
from typing import Any, Optional

# pylint:disable=cyclic-import      # but pylint doesn't understand this feature
from . import archivist

from .constants import (
    ASSETS_SUBPATH,
    ASSETS_WILDCARD,
    CONFIRMATION_STATUS,
    EVENTS_LABEL,
    SBOM_RELEASE,
)
from . import confirmer
from .dictmerge import _deepmerge
from .errors import ArchivistBadFieldError, ArchivistNotFoundError


LOGGER = getLogger(__name__)


class Event(dict):
    """Event

    Event object has dictionary attributes and properties.

    """

    @property
    def when(self) -> str | None:
        """when

        Timestamp of event

        """
        try:
            when: str = self["timestamp_declared"]
        except KeyError:
            pass
        else:
            return when

        try:
            when: str = self["timestamp_accepted"]
        except KeyError:
            pass
        else:
            return when

        return None

    @property
    def who(self) -> str | None:
        """who

        Principal identity.

        """

        try:
            who: str = self["principal_declared"]["display_name"]
        except (KeyError, TypeError):
            pass
        else:
            return who

        try:
            who: str = self["principal_accepted"]["display_name"]
        except (KeyError, TypeError):
            pass
        else:
            return who

        return None


class _EventsPublic:
    """EventsPublic

    Access to events entities using the CRUD interface. This class is usually
    accessed as an attribute of the Archivist class.

    Args:
        archivist (Archivist): :class:`Archivist` instance

    """

    def __init__(self, archivist_instance: archivist.Archivist):
        self._archivist = archivist_instance
        self._public = archivist_instance.public
        self._subpath = f"{archivist_instance.root}/{ASSETS_SUBPATH}"

    def __str__(self) -> str:
        return "EventsPublic()"

    def _identity(self, identity: str) -> str:
        """Return fully qualified identity
        If public then expect a full url as argument
        """

        if self._public:
            return identity

        return f"{self._subpath}/{identity}"

    def read(self, identity: str) -> Event:
        """Read event

        Reads event.

        Args:
            identity (str): events identity e.g. assets/xxxxxxx.../events/yyyyyyy...

        Returns:
            :class:`Event` instance

        """
        return Event(**self._archivist.get(f"{self._identity(identity)}"))

    def _params(
        self,
        props: Optional[dict[str, Any]],
        attrs: Optional[dict[str, Any]],
        asset_attrs: Optional[dict[str, Any]],
    ) -> dict[str, Any]:
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
        props: Optional[dict[str, Any]] = None,
        attrs: Optional[dict[str, Any]] = None,
        asset_attrs: Optional[dict[str, Any]] = None,
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

        # wildcarding not allowed when public - asset_id is required (not optional)
        # if asset_id is wildcarded a 401 will be returned from upstream
        if not self._public and not asset_id:
            asset_id = ASSETS_WILDCARD

        # The type checker rightly points out in the case of an event being public but with no
        # asset_id will cause issues in the _identity function and the count function
        LOGGER.debug("asset_id %s", asset_id)
        LOGGER.debug(
            "event_id %s", f"{self._identity(asset_id)}/{EVENTS_LABEL}"  # type:ignore
        )
        return self._archivist.count(
            f"{self._identity(asset_id)}/{EVENTS_LABEL}",  # type:ignore
            params=self._params(props, attrs, asset_attrs),
        )

    def list(
        self,
        *,
        asset_id: Optional[str] = None,
        page_size: Optional[int] = None,
        props: Optional[dict[str, Any]] = None,
        attrs: Optional[dict[str, Any]] = None,
        asset_attrs: Optional[dict[str, Any]] = None,
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
        # wildcarding not allowed when public - asset_id is required (not optional)
        # if asset_id is wildcarded a 401 will be returned from upstream
        if not self._public:
            asset_id = asset_id or ASSETS_WILDCARD

        return (
            Event(**a)
            for a in self._archivist.list(
                f"{self._identity(asset_id)}/{EVENTS_LABEL}",  # type:ignore
                EVENTS_LABEL,
                page_size=page_size,
                params=self._params(props, attrs, asset_attrs),
            )
        )

    def read_by_signature(
        self,
        *,
        asset_id: Optional[str] = None,
        props: Optional[dict[str, Any]] = None,
        attrs: Optional[dict[str, Any]] = None,
        asset_attrs: Optional[dict[str, Any]] = None,
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
        # wildcarding not allowed when public - asset_id is required (not optional)
        # if asset_id is wildcarded a 401 will be returned from upstream
        if not self._public:
            asset_id = asset_id or ASSETS_WILDCARD

        return Event(
            **self._archivist.get_by_signature(
                f"{self._identity(asset_id)}/{EVENTS_LABEL}",  # type:ignore
                EVENTS_LABEL,
                params=self._params(props, attrs, asset_attrs),
            )
        )


class _EventsRestricted(_EventsPublic):
    """EventsRestricted

    Access to events entities using the CRUD interface. This class is usually
    accessed as an attribute of the Archivist class.

    Args:
        archivist (Archivist): :class:`Archivist` instance

    """

    def __init__(self, archivist_instance: archivist.Archivist):
        super().__init__(archivist_instance)
        self.pending_count: int = 0

    def __str__(self) -> str:
        return f"EventsRestricted({self._archivist.url})"

    def create(
        self,
        asset_id: str,
        props: dict[str, Any],
        attrs: dict[str, Any],
        *,
        asset_attrs: Optional[dict[str, Any]] = None,
        confirm: bool = True,
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
            self._params(props, attrs, asset_attrs),
            confirm=confirm,
        )

    def create_from_data(
        self, asset_id: str, data: dict[str, Any], *, confirm: bool = True
    ) -> Event:
        """Create event

        Creates event for given asset from data.
        Suitable for reading data from json.load or yaml.load from a file

        Args:
            asset_id (str): asset identity e.g. assets/xxxxxxxxxxxxxxxxxxxxxxxxxx
            data (dict): request body of event.
            confirm (bool): if True wait for event to be confirmed.

        Returns:
            :class:`Event` instance

        """
        data = deepcopy(data)

        event_attributes = data["event_attributes"]
        # is location present?
        location = data.pop("location", None)
        if location is not None:
            if "identity" in location:
                data["event_attributes"]["arc_location_identity"] = location["identity"]
            else:
                loc, _ = self._archivist.locations.create_if_not_exists(
                    location,
                )
                event_attributes["arc_location_identity"] = loc["identity"]

        sbom = data.pop("sbom", None)
        if sbom is not None:
            sbom_result = self._archivist.sboms.create(sbom)
            for k, v in sbom_result.items():
                event_attributes[f"sbom_{k}"] = v

        attachments = data.pop("attachments", None)
        if attachments is not None:
            result = [self._archivist.attachments.create(a) for a in attachments]
            for i, a in enumerate(attachments):
                if a.get("type") == SBOM_RELEASE:
                    sbom_result = self._archivist.sboms.parse(a)
                    for k, v in sbom_result.items():
                        event_attributes[f"sbom_{k}"] = v

                    event_attributes["sbom_identity"] = result[i][
                        "arc_attachment_identity"
                    ]
                    break

            event_attributes["arc_attachments"] = result

        data["event_attributes"] = event_attributes

        event = Event(
            **self._archivist.post(f"{self._subpath}/{asset_id}/{EVENTS_LABEL}", data)
        )
        if not confirm:
            return event

        event_id: str = event["identity"]
        return self.wait_for_confirmation(event_id)

    def wait_for_confirmation(self, identity: str) -> Event:
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

    def wait_for_confirmed(
        self,
        *,
        asset_id: Optional[str] = None,
        props: Optional[dict[str, Any]] = None,
        attrs: Optional[dict[str, Any]] = None,
        asset_attrs: Optional[dict[str, Any]] = None,
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
        asset_id = asset_id or ASSETS_WILDCARD
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
            self,
            asset_id=asset_id,
            props=props,
            attrs=attrs,
            asset_attrs=asset_attrs,
        )

    def publicurl(self, identity: str) -> str:
        """Read event public url

        Reads event public url.

        Args:
            identity (str): events identity e.g. assets/xxxxxxx.../events/yyyyyyy...

        Returns:
            :str:public url as a string

        """
        body = self._archivist.get(f"{self._identity(identity)}:publicurl")
        publicurl = body.get("publicurl")
        if publicurl is None:
            raise ArchivistBadFieldError("No publicurl found in response")

        return publicurl
