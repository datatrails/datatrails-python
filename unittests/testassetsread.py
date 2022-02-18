"""
Test archivist
"""

from logging import getLogger
from os import environ

from unittest import mock

from archivist.constants import (
    HEADERS_REQUEST_TOTAL_COUNT,
    HEADERS_TOTAL_COUNT,
    ROOT,
)
from archivist.logger import set_logger

from .mock_response import MockResponse
from .testassetsconstants import (
    TestAssetsBase,
    IDENTITY,
    SUBPATH,
    RESPONSE,
    RESPONSE_NO_ATTACHMENTS,
)


# pylint: disable=missing-docstring
# pylint: disable=protected-access
# pylint: disable=unused-variable

if "TEST_DEBUG" in environ and environ["TEST_DEBUG"]:
    set_logger(environ["TEST_DEBUG"])

LOGGER = getLogger(__name__)


class TestAssetsRead(TestAssetsBase):
    """
    Test Archivist Assets methods
    """

    def test_assets_read_with_out_primary_image(self):
        """
        Test asset reading
        """
        with mock.patch.object(self.arch._session, "get") as mock_get:
            mock_get.return_value = MockResponse(200, **RESPONSE_NO_ATTACHMENTS)

            asset = self.arch.assets.read(IDENTITY)
            self.assertEqual(
                asset,
                RESPONSE_NO_ATTACHMENTS,
                msg="READ method called incorrectly",
            )
            self.assertIsNone(
                asset.primary_image,
                msg="There should be no primary image",
            )
            self.assertIsNone(
                asset.name,
                msg="There should be no name property",
            )


class TestAssetsCount(TestAssetsBase):
    """
    Test Archivist Assets methods
    """

    def test_assets_count(self):
        """
        Test asset counting
        """
        with mock.patch.object(self.arch._session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                headers={HEADERS_TOTAL_COUNT: 1},
                assets=[
                    RESPONSE,
                ],
            )

            count = self.arch.assets.count()
            self.assertEqual(
                count,
                1,
                msg="Incorrect count",
            )
            self.assertEqual(
                tuple(mock_get.call_args),
                (
                    ((f"url/{ROOT}/{SUBPATH}"),),
                    {
                        "headers": {
                            "authorization": "Bearer authauthauth",
                            HEADERS_REQUEST_TOTAL_COUNT: "true",
                        },
                        "params": {"page_size": 1},
                        "verify": True,
                    },
                ),
                msg="GET method called incorrectly",
            )

    def test_assets_count_with_props_params(self):
        """
        Test asset counting
        """
        with mock.patch.object(self.arch._session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                headers={HEADERS_TOTAL_COUNT: 1},
                assets=[
                    RESPONSE,
                ],
            )

            count = self.arch.assets.count(
                props={
                    "confirmation_status": "CONFIRMED",
                },
            )
            self.assertEqual(
                tuple(mock_get.call_args),
                (
                    ((f"url/{ROOT}/{SUBPATH}"),),
                    {
                        "headers": {
                            "authorization": "Bearer authauthauth",
                            HEADERS_REQUEST_TOTAL_COUNT: "true",
                        },
                        "params": {
                            "page_size": 1,
                            "confirmation_status": "CONFIRMED",
                        },
                        "verify": True,
                    },
                ),
                msg="GET method called incorrectly",
            )

    def test_assets_count_with_attrs_params(self):
        """
        Test asset counting
        """
        with mock.patch.object(self.arch._session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                headers={HEADERS_TOTAL_COUNT: 1},
                assets=[
                    RESPONSE,
                ],
            )

            count = self.arch.assets.count(
                attrs={"arc_firmware_version": "1.0"},
            )
            self.assertEqual(
                tuple(mock_get.call_args),
                (
                    ((f"url/{ROOT}/{SUBPATH}"),),
                    {
                        "headers": {
                            "authorization": "Bearer authauthauth",
                            HEADERS_REQUEST_TOTAL_COUNT: "true",
                        },
                        "params": {
                            "page_size": 1,
                            "attributes.arc_firmware_version": "1.0",
                        },
                        "verify": True,
                    },
                ),
                msg="GET method called incorrectly",
            )
