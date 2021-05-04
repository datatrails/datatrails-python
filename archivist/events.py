"""events interface
"""

from copy import deepcopy

from .constants import (
    SEP,
    ASSETS_SUBPATH,
    ASSETS_WILDCARD,
    EVENTS_LABEL,
)
from .confirm import wait_for_confirmation, wait_for_confirmed

DEFAULT_PAGE_SIZE = 500


class _EventsClient:
    """docstring"""

    def __init__(self, archivist):
        """docstring"""
        self._archivist = archivist

    def create(self, asset_id, props, attrs, *, asset_attrs=None, confirm=False):
        """docstring"""
        return self.create_from_data(
            asset_id,
            self.__query(props, attrs, asset_attrs),
            confirm=confirm,
        )

    def create_from_data(self, asset_id, data, *, confirm=False):
        """docstring

        read request from data stream
        suitable for reading data from json.load,yaml.load from a file
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
        """docstring"""
        return Event(
            **self._archivist.get(
                ASSETS_SUBPATH,
                identity,
            )
        )

    @staticmethod
    def __query(props, attrs, asset_attrs):
        """docstring"""
        query = deepcopy(props) if props else {}
        if attrs:
            query["event_attributes"] = attrs
        if asset_attrs:
            query["asset_attributes"] = asset_attrs

        return query

    def count(
        self, *, asset_id=ASSETS_WILDCARD, props=None, attrs=None, asset_attrs=None
    ):
        """docstring"""
        return self._archivist.count(
            SEP.join((ASSETS_SUBPATH, asset_id, EVENTS_LABEL)),
            query=self.__query(props, attrs, asset_attrs),
        )

    def wait_for_confirmed(self, *, asset_id=ASSETS_WILDCARD, props=None, attrs=None):
        """docstring"""
        return wait_for_confirmed(self, asset_id=asset_id, props=props, attrs=attrs)

    def list(
        self,
        *,
        asset_id=ASSETS_WILDCARD,
        page_size=DEFAULT_PAGE_SIZE,
        props=None,
        attrs=None,
        asset_attrs=None,
    ):
        """docstring"""
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
        """docstring"""
        return Event(
            **self._archivist.get_by_signature(
                SEP.join((ASSETS_SUBPATH, asset_id, EVENTS_LABEL)),
                EVENTS_LABEL,
                query=self.__query(props, attrs, asset_attrs),
            )
        )


class Event(dict):
    """docstring"""

    @property
    def when(self):
        """docstring"""
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
        """docstring"""

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
