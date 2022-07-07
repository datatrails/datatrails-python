"""
Test assets read
"""

from logging import getLogger
from os import environ

from unittest import mock

from archivist.constants import (
    HEADERS_REQUEST_TOTAL_COUNT,
    HEADERS_TOTAL_COUNT,
    ROOT,
)
from archivist.errors import ArchivistBadFieldError
from archivist.logger import set_logger

from .mock_response import MockResponse
from .testassetsconstants import (
    TestAssetsBase,
    IDENTITY,
    SUBPATH,
    RESPONSE,
    RESPONSE_NO_ATTACHMENTS,
)

PUBLICURL = (
    "https://app.rkvst.io/archivist/publicassets/13f23360-14c7-4d00-ac29-0a862584060e"
)
RESPONSE_PUBLICURL = {
    "publicurl": PUBLICURL,
}
RESPONSE_BAD_PUBLICURL = {
    "badpublicurl": PUBLICURL,
}

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
        with mock.patch.object(self.arch.session, "get") as mock_get:
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

    def test_assets_publicurl(self):
        """
        Test asset reading publicurl
        """
        with mock.patch.object(self.arch.session, "get") as mock_get:
            mock_get.return_value = MockResponse(200, **RESPONSE_PUBLICURL)

            publicurl = self.arch.assets.publicurl(IDENTITY)
            self.assertEqual(
                publicurl,
                PUBLICURL,
                msg="Public url is incorrect",
            )

    def test_assets_publicurl_bad_response(self):
        """
        Test asset reading publicurl with bad response
        """
        with mock.patch.object(self.arch.session, "get") as mock_get:
            mock_get.return_value = MockResponse(200, **RESPONSE_BAD_PUBLICURL)

            with self.assertRaises(ArchivistBadFieldError):
                publicurl = self.arch.assets.publicurl(IDENTITY)


class TestAssetsCount(TestAssetsBase):
    """
    Test Archivist Assets methods
    """

    def test_assets_count(self):
        """
        Test asset counting
        """
        with mock.patch.object(self.arch.session, "get") as mock_get:
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
        with mock.patch.object(self.arch.session, "get") as mock_get:
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
        with mock.patch.object(self.arch.session, "get") as mock_get:
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
