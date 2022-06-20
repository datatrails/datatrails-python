"""
Test public events
"""

from logging import getLogger
from os import environ
from unittest import mock, TestCase

from archivist.archivistpublic import ArchivistPublic
from archivist.constants import (
    EVENTS_LABEL,
    HEADERS_REQUEST_TOTAL_COUNT,
    HEADERS_TOTAL_COUNT,
    PUBLICASSETS_LABEL,
    ROOT,
)
from archivist.logger import set_logger

from .testeventsconstants import (
    ASSET_ATTRS,
    ASSET_ID,
    RESPONSE,
)
from .mock_response import MockResponse
from .testevents import IDENTITY

if "TEST_DEBUG" in environ and environ["TEST_DEBUG"]:
    set_logger(environ["TEST_DEBUG"])

LOGGER = getLogger(__name__)


URL = "https://app.rkvst.io"
EVENT_IDENTITY = f"{URL}/{ROOT}/public{IDENTITY}"
ASSET_IDENTITY = f"{URL}/{ROOT}/public{ASSET_ID}"

EVENT_IDENTITY_NO_SUBPATH = f"{URL}/{ROOT}/public{IDENTITY}"
ASSET_IDENTITY_NO_SUBPATH = f"{URL}/{ROOT}/public{ASSET_ID}"

# pylint: disable=protected-access


class TestPublicEvents(TestCase):
    """
    Test Archivist PublicEvents Create method
    """

    maxDiff = None

    def setUp(self):
        self.public = ArchivistPublic(max_time=1)

    def tearDown(self):
        self.public.close()

    def test_publicevents_str(self):
        """
        Test events str
        """
        self.assertEqual(
            str(self.public.events),
            "EventsPublic()",
            msg="Incorrect str",
        )

    def test_publicevents_read(self):
        """
        Test publicevent reading
        """
        with mock.patch.object(self.public.session, "get") as mock_get:
            mock_get.return_value = MockResponse(200, **RESPONSE)

            event = self.public.events.read(EVENT_IDENTITY)
            self.assertEqual(
                tuple(mock_get.call_args),
                (
                    (
                        (
                            f"{URL}/{ROOT}"
                            f"/{PUBLICASSETS_LABEL}/xxxxxxxxxxxxxxxxxxxx"
                            f"/{EVENTS_LABEL}/xxxxxxxxxxxxxxxxxxxx"
                        ),
                    ),
                    {
                        "headers": {},
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

    def test_publicevents_read_no_subpath(self):
        """
        Test publicevent reading
        """
        with mock.patch.object(self.public.session, "get") as mock_get:
            mock_get.return_value = MockResponse(200, **RESPONSE)

            event = self.public.events.read(EVENT_IDENTITY_NO_SUBPATH)
            self.assertEqual(
                tuple(mock_get.call_args),
                (
                    (
                        (
                            f"{URL}/{ROOT}"
                            f"/{PUBLICASSETS_LABEL}/xxxxxxxxxxxxxxxxxxxx"
                            f"/{EVENTS_LABEL}/xxxxxxxxxxxxxxxxxxxx"
                        ),
                    ),
                    {
                        "headers": {},
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

    def test_publicevents_count(self):
        """
        Test event counting
        """
        with mock.patch.object(self.public.session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                headers={HEADERS_TOTAL_COUNT: 1},
                events=[
                    RESPONSE,
                ],
            )

            count = self.public.events.count(
                asset_id=ASSET_IDENTITY,
                asset_attrs=ASSET_ATTRS,
                attrs={"arc_firmware_version": "1.0"},
            )
            self.assertEqual(
                count,
                1,
                msg="Incorrect count",
            )
            self.assertEqual(
                tuple(mock_get.call_args),
                (
                    (
                        (
                            f"{URL}/{ROOT}"
                            f"/{PUBLICASSETS_LABEL}/xxxxxxxxxxxxxxxxxxxx"
                            f"/{EVENTS_LABEL}"
                        ),
                    ),
                    {
                        "headers": {
                            HEADERS_REQUEST_TOTAL_COUNT: "true",
                        },
                        "params": {
                            "asset_attributes.external_container": "assets/xxxx",
                            "event_attributes.arc_firmware_version": "1.0",
                            "page_size": 1,
                        },
                        "verify": True,
                    },
                ),
                msg="GET method called incorrectly",
            )

    def test_publicevents_count_no_subpath(self):
        """
        Test event counting
        """
        with mock.patch.object(self.public.session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                headers={HEADERS_TOTAL_COUNT: 1},
                events=[
                    RESPONSE,
                ],
            )

            count = self.public.events.count(
                asset_id=ASSET_IDENTITY_NO_SUBPATH,
                asset_attrs=ASSET_ATTRS,
                attrs={"arc_firmware_version": "1.0"},
            )
            self.assertEqual(
                count,
                1,
                msg="Incorrect count",
            )
            self.assertEqual(
                tuple(mock_get.call_args),
                (
                    (
                        (
                            f"{URL}/{ROOT}"
                            f"/{PUBLICASSETS_LABEL}/xxxxxxxxxxxxxxxxxxxx"
                            f"/{EVENTS_LABEL}"
                        ),
                    ),
                    {
                        "headers": {
                            HEADERS_REQUEST_TOTAL_COUNT: "true",
                        },
                        "params": {
                            "asset_attributes.external_container": "assets/xxxx",
                            "event_attributes.arc_firmware_version": "1.0",
                            "page_size": 1,
                        },
                        "verify": True,
                    },
                ),
                msg="GET method called incorrectly",
            )

    def test_publicevents_list(self):
        """
        Test publicevent listing
        """
        with mock.patch.object(self.public.session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                events=[
                    RESPONSE,
                ],
            )

            events = list(self.public.events.list(asset_id=ASSET_IDENTITY))
            self.assertEqual(
                len(events),
                1,
                msg="incorrect number of events",
            )
            for event in events:
                self.assertEqual(
                    event,
                    RESPONSE,
                    msg="Incorrect event listed",
                )

            for a in mock_get.call_args_list:
                self.assertEqual(
                    tuple(a),
                    (
                        (
                            (
                                f"{URL}/{ROOT}"
                                f"/{PUBLICASSETS_LABEL}/xxxxxxxxxxxxxxxxxxxx"
                                f"/{EVENTS_LABEL}"
                            ),
                        ),
                        {
                            "headers": {},
                            "params": {},
                            "verify": True,
                        },
                    ),
                    msg="GET method called incorrectly",
                )

    def test_publicevents_list_no_subpath(self):
        """
        Test publicevent listing
        """
        with mock.patch.object(self.public.session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                events=[
                    RESPONSE,
                ],
            )

            events = list(self.public.events.list(asset_id=ASSET_IDENTITY_NO_SUBPATH))
            self.assertEqual(
                len(events),
                1,
                msg="incorrect number of events",
            )
            for event in events:
                self.assertEqual(
                    event,
                    RESPONSE,
                    msg="Incorrect event listed",
                )

            for a in mock_get.call_args_list:
                self.assertEqual(
                    tuple(a),
                    (
                        (
                            (
                                f"{URL}/{ROOT}"
                                f"/{PUBLICASSETS_LABEL}/xxxxxxxxxxxxxxxxxxxx"
                                f"/{EVENTS_LABEL}"
                            ),
                        ),
                        {
                            "headers": {},
                            "params": {},
                            "verify": True,
                        },
                    ),
                    msg="GET method called incorrectly",
                )

    def test_publicevents_read_by_signature(self):
        """
        Test publicevent listing
        """
        with mock.patch.object(self.public.session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                events=[
                    RESPONSE,
                ],
            )

            event = self.public.events.read_by_signature(asset_id=ASSET_IDENTITY)
            self.assertEqual(
                event,
                RESPONSE,
                msg="Incorrect event listed",
            )

            self.assertEqual(
                tuple(mock_get.call_args),
                (
                    (
                        (
                            f"{URL}/{ROOT}"
                            f"/{PUBLICASSETS_LABEL}/xxxxxxxxxxxxxxxxxxxx"
                            f"/{EVENTS_LABEL}"
                        ),
                    ),
                    {
                        "headers": {},
                        "params": {"page_size": 2},
                        "verify": True,
                    },
                ),
                msg="GET method called incorrectly",
            )
