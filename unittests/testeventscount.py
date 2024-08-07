"""
Test events count
"""

from unittest import mock

from archivist.about import __version__ as VERSION
from archivist.constants import (
    ASSETS_LABEL,
    ASSETS_SUBPATH,
    ASSETS_WILDCARD,
    EVENTS_LABEL,
    HEADERS_REQUEST_TOTAL_COUNT,
    HEADERS_TOTAL_COUNT,
    ROOT,
    USER_AGENT,
    USER_AGENT_PREFIX,
)

from .mock_response import MockResponse
from .testeventsconstants import (
    ASSET_ID,
    RESPONSE,
    TestEventsBase,
)

# pylint: disable=missing-docstring
# pylint: disable=protected-access
# pylint: disable=unused-variable
# pylint: disable=too-many-public-methods


class TestEventsCount(TestEventsBase):
    """
    Test Archivist Events Count method
    """

    def test_events_count(self):
        """
        Test event counting
        """
        with mock.patch.object(self.arch.session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                headers={HEADERS_TOTAL_COUNT: 1},
                events=[
                    RESPONSE,
                ],
            )

            count = self.arch.events.count(asset_id=ASSET_ID)
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
                            f"url/{ROOT}/{ASSETS_SUBPATH}"
                            f"/{ASSETS_LABEL}/xxxxxxxxxxxxxxxxxxxx"
                            f"/{EVENTS_LABEL}"
                        ),
                    ),
                    {
                        "headers": {
                            "authorization": "Bearer authauthauth",
                            HEADERS_REQUEST_TOTAL_COUNT: "true",
                            USER_AGENT: f"{USER_AGENT_PREFIX}{VERSION}",
                        },
                        "params": {"page_size": 1},
                    },
                ),
                msg="GET method called incorrectly",
            )

    def test_events_count_with_props_params(self):
        """
        Test event counting
        """
        with mock.patch.object(self.arch.session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                headers={HEADERS_TOTAL_COUNT: 1},
                events=[
                    RESPONSE,
                ],
            )

            self.arch.events.count(
                asset_id=ASSET_ID,
                props={
                    "confirmation_status": "CONFIRMED",
                },
            )
            self.assertEqual(
                tuple(mock_get.call_args),
                (
                    (
                        (
                            f"url/{ROOT}/{ASSETS_SUBPATH}"
                            f"/{ASSETS_LABEL}/xxxxxxxxxxxxxxxxxxxx"
                            f"/{EVENTS_LABEL}"
                        ),
                    ),
                    {
                        "headers": {
                            "authorization": "Bearer authauthauth",
                            HEADERS_REQUEST_TOTAL_COUNT: "true",
                            USER_AGENT: f"{USER_AGENT_PREFIX}{VERSION}",
                        },
                        "params": {"page_size": 1, "confirmation_status": "CONFIRMED"},
                    },
                ),
                msg="GET method called incorrectly",
            )

    def test_events_count_with_attrs_params(self):
        """
        Test event counting
        """
        with mock.patch.object(self.arch.session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                headers={HEADERS_TOTAL_COUNT: 1},
                events=[
                    RESPONSE,
                ],
            )

            self.arch.events.count(
                asset_id=ASSET_ID,
                attrs={"arc_firmware_version": "1.0"},
            )
            self.assertEqual(
                tuple(mock_get.call_args),
                (
                    (
                        (
                            f"url/{ROOT}/{ASSETS_SUBPATH}"
                            f"/{ASSETS_LABEL}/xxxxxxxxxxxxxxxxxxxx"
                            f"/{EVENTS_LABEL}"
                        ),
                    ),
                    {
                        "headers": {
                            "authorization": "Bearer authauthauth",
                            HEADERS_REQUEST_TOTAL_COUNT: "true",
                            USER_AGENT: f"{USER_AGENT_PREFIX}{VERSION}",
                        },
                        "params": {
                            "page_size": 1,
                            "event_attributes.arc_firmware_version": "1.0",
                        },
                    },
                ),
                msg="GET method called incorrectly",
            )

    def test_events_count_with_wildcard_asset(self):
        """
        Test event counting
        """
        with mock.patch.object(self.arch.session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                headers={HEADERS_TOTAL_COUNT: 1},
                events=[
                    RESPONSE,
                ],
            )

            self.arch.events.count(
                attrs={"arc_firmware_version": "1.0"},
            )
            self.assertEqual(
                tuple(mock_get.call_args),
                (
                    (
                        (
                            f"url/{ROOT}/{ASSETS_SUBPATH}"
                            f"/{ASSETS_WILDCARD}"
                            f"/{EVENTS_LABEL}"
                        ),
                    ),
                    {
                        "headers": {
                            "authorization": "Bearer authauthauth",
                            HEADERS_REQUEST_TOTAL_COUNT: "true",
                            USER_AGENT: f"{USER_AGENT_PREFIX}{VERSION}",
                        },
                        "params": {
                            "page_size": 1,
                            "event_attributes.arc_firmware_version": "1.0",
                        },
                    },
                ),
                msg="GET method called incorrectly",
            )
