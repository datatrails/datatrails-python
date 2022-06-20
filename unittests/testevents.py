"""
Test archivist
"""

from unittest import TestCase, mock

from archivist.constants import (
    ROOT,
    ASSETS_LABEL,
    ASSETS_SUBPATH,
    EVENTS_LABEL,
)
from archivist.events import Event

from .mock_response import MockResponse
from .testeventsconstants import (
    TestEventsBase,
    IDENTITY,
    RESPONSE,
    RESPONSE_WITH_NO_PRINCIPAL,
    RESPONSE_WITH_PRINCIPAL_DECLARED,
    RESPONSE_WITH_TIMESTAMP_ACCEPTED,
    RESPONSE_WITH_NO_TIMESTAMP,
)

# pylint: disable=missing-docstring
# pylint: disable=protected-access
# pylint: disable=unused-variable
# pylint: disable=too-many-public-methods


class TestEvent(TestCase):
    """
    Test Archivist Events Create method
    """

    maxDiff = None

    def test_event_who_accepted(self):
        event = Event(**RESPONSE)
        self.assertEqual(
            event.who,
            "Accepted",
            msg="Incorrect who",
        )

    def test_event_who_none(self):
        event = Event(**RESPONSE_WITH_NO_PRINCIPAL)
        self.assertEqual(
            event.who,
            None,
            msg="who should be None",
        )

    def test_event_who_declared(self):
        event = Event(**RESPONSE_WITH_PRINCIPAL_DECLARED)
        self.assertEqual(
            event.who,
            "Declared",
            msg="Incorrect who",
        )

    def test_event_when_declared(self):
        event = Event(**RESPONSE)
        self.assertEqual(
            event.when,
            "2019-11-27T14:44:19Z",
            msg="Incorrect when",
        )

    def test_event_when_accepted(self):
        event = Event(**RESPONSE_WITH_TIMESTAMP_ACCEPTED)
        self.assertEqual(
            event.when,
            "2021-04-08T14:44:19Z",
            msg="Incorrect when",
        )

    def test_event_when_none(self):
        event = Event(**RESPONSE_WITH_NO_TIMESTAMP)
        self.assertEqual(
            event.when,
            None,
            msg="Incorrect when",
        )


class TestEventsRead(TestEventsBase):
    """
    Test Archivist Events Read method
    """

    def test_events_read(self):
        """
        Test event reading
        """
        with mock.patch.object(self.arch.session, "get") as mock_get:
            mock_get.return_value = MockResponse(200, **RESPONSE)

            event = self.arch.events.read(IDENTITY)
            self.assertEqual(
                tuple(mock_get.call_args),
                (
                    (
                        (
                            f"url/{ROOT}/{ASSETS_SUBPATH}"
                            f"/{ASSETS_LABEL}/xxxxxxxxxxxxxxxxxxxx"
                            f"/{EVENTS_LABEL}/xxxxxxxxxxxxxxxxxxxx"
                        ),
                    ),
                    {
                        "headers": {
                            "authorization": "Bearer authauthauth",
                        },
                        "params": None,
                        "verify": True,
                    },
                ),
                msg="GET method called incorrectly",
            )
            self.assertEqual(
                event,
                RESPONSE,
                msg="GET method called incorrectly",
            )

    def test_events_read_with_no_principal(self):
        """
        Test event reading
        """
        with mock.patch.object(self.arch.session, "get") as mock_get:
            mock_get.return_value = MockResponse(200, **RESPONSE)

            event = self.arch.events.read(IDENTITY)
            self.assertEqual(
                event,
                RESPONSE,
                msg="GET method called incorrectly",
            )
