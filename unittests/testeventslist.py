"""
Test events list
"""

from unittest import mock

from archivist.constants import (
    ASSETS_LABEL,
    ASSETS_SUBPATH,
    ASSETS_WILDCARD,
    EVENTS_LABEL,
    ROOT,
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


class TestEventsList(TestEventsBase):
    """
    Test Archivist Events Read method
    """

    def test_events_list(self):
        """
        Test event listing
        """
        with mock.patch.object(self.arch.session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                events=[
                    RESPONSE,
                ],
            )

            events = list(self.arch.events.list(asset_id=ASSET_ID))
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
                                f"url/{ROOT}/{ASSETS_SUBPATH}"
                                f"/{ASSETS_LABEL}/xxxxxxxxxxxxxxxxxxxx"
                                f"/{EVENTS_LABEL}"
                            ),
                        ),
                        {
                            "headers": {
                                "authorization": "Bearer authauthauth",
                            },
                            "params": {},
                            "verify": True,
                        },
                    ),
                    msg="GET method called incorrectly",
                )

    def test_events_list_with_params(self):
        """
        Test event listing
        """
        with mock.patch.object(self.arch.session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                events=[
                    RESPONSE,
                ],
            )

            events = list(
                self.arch.events.list(
                    asset_id=ASSET_ID,
                    props={
                        "confirmation_status": "CONFIRMED",
                    },
                    attrs={"arc_firmware_version": "1.0"},
                )
            )
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
                                f"url/{ROOT}/{ASSETS_SUBPATH}"
                                f"/{ASSETS_LABEL}/xxxxxxxxxxxxxxxxxxxx"
                                f"/{EVENTS_LABEL}"
                            ),
                        ),
                        {
                            "headers": {
                                "authorization": "Bearer authauthauth",
                            },
                            "params": {
                                "confirmation_status": "CONFIRMED",
                                "event_attributes.arc_firmware_version": "1.0",
                            },
                            "verify": True,
                        },
                    ),
                    msg="GET method called incorrectly",
                )

    def test_events_list_with_wildcard_asset(self):
        """
        Test event listing
        """
        with mock.patch.object(self.arch.session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                events=[
                    RESPONSE,
                ],
            )

            events = list(
                self.arch.events.list(
                    props={
                        "confirmation_status": "CONFIRMED",
                    },
                    attrs={"arc_firmware_version": "1.0"},
                )
            )
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
                                f"url/{ROOT}/{ASSETS_SUBPATH}"
                                f"/{ASSETS_WILDCARD}"
                                f"/{EVENTS_LABEL}"
                            ),
                        ),
                        {
                            "headers": {
                                "authorization": "Bearer authauthauth",
                            },
                            "params": {
                                "confirmation_status": "CONFIRMED",
                                "event_attributes.arc_firmware_version": "1.0",
                            },
                            "verify": True,
                        },
                    ),
                    msg="GET method called incorrectly",
                )

    def test_events_read_by_signature(self):
        """
        Test event listing
        """
        with mock.patch.object(self.arch.session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                events=[
                    RESPONSE,
                ],
            )

            event = self.arch.events.read_by_signature(asset_id=ASSET_ID)
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
                            f"url/{ROOT}/{ASSETS_SUBPATH}"
                            f"/{ASSETS_LABEL}/xxxxxxxxxxxxxxxxxxxx"
                            f"/{EVENTS_LABEL}"
                        ),
                    ),
                    {
                        "headers": {
                            "authorization": "Bearer authauthauth",
                        },
                        "params": {"page_size": 2},
                        "verify": True,
                    },
                ),
                msg="GET method called incorrectly",
            )
