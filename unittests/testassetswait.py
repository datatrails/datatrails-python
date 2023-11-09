"""
Test assets wait
"""

from logging import getLogger
from os import environ
from unittest import mock

from archivist.constants import (
    HEADERS_REQUEST_TOTAL_COUNT,
    HEADERS_TOTAL_COUNT,
    ROOT,
)
from archivist.errors import ArchivistNotFoundError, ArchivistUnconfirmedError
from archivist.logger import set_logger

from .mock_response import MockResponse
from .testassetsconstants import (
    RESPONSE_FAILED,
    RESPONSE_PENDING,
    SUBPATH,
    TestAssetsBase,
)

# pylint: disable=missing-docstring
# pylint: disable=protected-access
# pylint: disable=unused-variable

if "DATATRAILS_LOGLEVEL" in environ and environ["DATATRAILS_LOGLEVEL"]:
    set_logger(environ["DATATRAILS_LOGLEVEL"])

LOGGER = getLogger(__name__)


class TestAssetsWait(TestAssetsBase):
    """
    Test Archivist Assets methods
    """

    def test_assets_wait_for_confirmed(self):
        """
        Test asset counting
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

            self.arch.assets.wait_for_confirmed()
            for i, a in enumerate(mock_get.call_args_list):
                self.assertEqual(
                    tuple(a),
                    (
                        (f"url/{ROOT}/{SUBPATH}",),
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

    def test_assets_wait_for_confirmed_not_found(self):
        """
        Test asset counting
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
                self.arch.assets.wait_for_confirmed()

    def test_assets_wait_for_confirmed_timeout(self):
        """
        Test asset counting
        """
        ## last call to get looks for FAILED assets
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
                    headers={HEADERS_TOTAL_COUNT: 2},
                    assets=[
                        RESPONSE_PENDING,
                    ],
                ),
                MockResponse(
                    200,
                    headers={HEADERS_TOTAL_COUNT: 2},
                    assets=[
                        RESPONSE_PENDING,
                    ],
                ),
                MockResponse(
                    200,
                    headers={HEADERS_TOTAL_COUNT: 2},
                    assets=[
                        RESPONSE_PENDING,
                    ],
                ),
                MockResponse(
                    200,
                    headers={HEADERS_TOTAL_COUNT: 2},
                    assets=[
                        RESPONSE_PENDING,
                    ],
                ),
                MockResponse(
                    200,
                    headers={HEADERS_TOTAL_COUNT: 2},
                    assets=[
                        RESPONSE_PENDING,
                    ],
                ),
            ]

            with self.assertRaises(ArchivistUnconfirmedError):
                self.arch.assets.wait_for_confirmed()

    def test_assets_wait_for_confirmed_failed(self):
        """
        Test asset counting
        """
        ## last call to get looks for FAILED assets
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
                    headers={HEADERS_TOTAL_COUNT: 1},
                    assets=[
                        RESPONSE_FAILED,
                    ],
                ),
            ]

            with self.assertRaises(ArchivistUnconfirmedError):
                self.arch.assets.wait_for_confirmed()
