"""
Test archivist
"""

from unittest import mock

from archivist.constants import (
    ROOT,
    ASSETS_WILDCARD,
    ASSETS_SUBPATH,
    EVENTS_LABEL,
    HEADERS_REQUEST_TOTAL_COUNT,
    HEADERS_TOTAL_COUNT,
)
from archivist.errors import (
    ArchivistNotFoundError,
)

from .mock_response import MockResponse
from .testeventsconstants import (
    TestEventsBase,
    RESPONSE_PENDING,
)

# pylint: disable=missing-docstring
# pylint: disable=protected-access
# pylint: disable=unused-variable
# pylint: disable=too-many-public-methods


class TestEventsWait(TestEventsBase):
    """
    Test Archivist Events wait method
    """

    def test_events_wait_for_confirmed(self):
        """
        Test event counting
        """
        ## last call to get looks for FAILED assets
        status = (
            {"page_size": 1},
            {"page_size": 1, "confirmation_status": "PENDING"},
            {"page_size": 1, "confirmation_status": "FAILED"},
        )
        with mock.patch.object(self.arch.session, "get") as mock_get:
            mock_get.side_effect = [
                MockResponse(
                    200,
                    headers={HEADERS_TOTAL_COUNT: 2},
                    assets=[
                        RESPONSE_PENDING,
                    ],
                ),
                MockResponse(
                    200,
                    headers={HEADERS_TOTAL_COUNT: 0},
                    assets=[],
                ),
                MockResponse(
                    200,
                    headers={HEADERS_TOTAL_COUNT: 0},
                    assets=[],
                ),
            ]

            self.arch.events.wait_for_confirmed()
            for i, a in enumerate(mock_get.call_args_list):
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
                                HEADERS_REQUEST_TOTAL_COUNT: "true",
                            },
                            "params": status[i],
                            "verify": True,
                        },
                    ),
                    msg="GET method called incorrectly",
                )

    def test_events_wait_for_confirmed_not_found(self):
        """
        Test event counting
        """
        with mock.patch.object(self.arch.session, "get") as mock_get:
            mock_get.side_effect = [
                MockResponse(
                    200,
                    headers={HEADERS_TOTAL_COUNT: 0},
                    assets=[
                        RESPONSE_PENDING,
                    ],
                ),
            ]

            with self.assertRaises(ArchivistNotFoundError):
                self.arch.events.wait_for_confirmed()
