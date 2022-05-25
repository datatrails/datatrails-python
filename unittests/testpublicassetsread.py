"""
Test archivist
"""

from logging import getLogger
from os import environ

from unittest import mock

from archivist.logger import set_logger
from .mock_response import MockResponse
from .testassetsconstants import (
    IDENTITY,
    RESPONSE_NO_ATTACHMENTS,
)
from .testpublicassets import TestPublicAssetsBase


# pylint: disable=missing-docstring
# pylint: disable=protected-access
# pylint: disable=unused-variable

if "TEST_DEBUG" in environ and environ["TEST_DEBUG"]:
    set_logger(environ["TEST_DEBUG"])

LOGGER = getLogger(__name__)


class TestPublicAssetsRead(TestPublicAssetsBase):
    """
    Test Archivist Public Assets methods
    """

    def test_public_assets_read_with_out_primary_image(self):
        """
        Test public asset reading
        """
        with mock.patch.object(self.arch._session, "get") as mock_get:
            mock_get.return_value = MockResponse(200, **RESPONSE_NO_ATTACHMENTS)

            asset = self.arch.publicassets.read(IDENTITY)
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
