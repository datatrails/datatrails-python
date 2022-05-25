"""
Test archivist
"""

from unittest import mock, TestCase

from archivist.archivist import Archivist
from archivist.constants import (
    EVENTS_LABEL,
    HEADERS_REQUEST_TOTAL_COUNT,
    HEADERS_TOTAL_COUNT,
    PUBLICASSETS_LABEL,
    PUBLICASSETS_SUBPATH,
    ROOT,
)

from .testevents import (
    ASSET_ATTRS,
    ASSET_ID,
    RESPONSE,
)
from .mock_response import MockResponse
from .testevents import IDENTITY

# pylint: disable=protected-access


class TestPublicEvents(TestCase):
    """
    Test Archivist PublicEvents Create method
    """

    maxDiff = None

    def setUp(self):
        self.arch = Archivist("url", None, max_time=1)

    def tearDown(self):
        self.arch = None

    def test_publicevents_str(self):
        """
        Test events str
        """
        self.assertEqual(
            str(self.arch.publicevents),
            "PublicEventsClient(url)",
            msg="Incorrect str",
        )

    def test_publicevents_read(self):
        """
        Test publicevent reading
        """
        with mock.patch.object(self.arch._session, "get") as mock_get:
            mock_get.return_value = MockResponse(200, **RESPONSE)

            event = self.arch.publicevents.read(IDENTITY)
            self.assertEqual(
                tuple(mock_get.call_args),
                (
                    (
                        (
                            f"url/{ROOT}/{PUBLICASSETS_SUBPATH}"
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
        with mock.patch.object(self.arch._session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                headers={HEADERS_TOTAL_COUNT: 1},
                events=[
                    RESPONSE,
                ],
            )

            count = self.arch.publicevents.count(
                asset_id=ASSET_ID,
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
                            f"url/{ROOT}/{PUBLICASSETS_SUBPATH}"
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
        with mock.patch.object(self.arch._session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                events=[
                    RESPONSE,
                ],
            )

            events = list(self.arch.publicevents.list(asset_id=f"public{ASSET_ID}"))
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
                                f"url/{ROOT}/{PUBLICASSETS_SUBPATH}"
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
        with mock.patch.object(self.arch._session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                events=[
                    RESPONSE,
                ],
            )

            event = self.arch.publicevents.read_by_signature(asset_id=ASSET_ID)
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
                            f"url/{ROOT}/{PUBLICASSETS_SUBPATH}"
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
