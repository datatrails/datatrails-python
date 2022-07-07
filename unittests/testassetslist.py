"""
Test assets list
"""

from logging import getLogger
from os import environ

from unittest import mock

from archivist.constants import (
    ROOT,
)
from archivist.logger import set_logger

from .mock_response import MockResponse
from .testassetsconstants import (
    TestAssetsBase,
    SUBPATH,
    RESPONSE,
)

# pylint: disable=missing-docstring
# pylint: disable=protected-access
# pylint: disable=unused-variable

if "TEST_DEBUG" in environ and environ["TEST_DEBUG"]:
    set_logger(environ["TEST_DEBUG"])

LOGGER = getLogger(__name__)


class TestAssetsList(TestAssetsBase):
    """
    Test Archivist Assets methods
    """

    def test_assets_list(self):
        """
        Test asset listing
        """
        with mock.patch.object(self.arch.session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                assets=[
                    RESPONSE,
                ],
            )

            assets = list(self.arch.assets.list())
            self.assertEqual(
                len(assets),
                1,
                msg="incorrect number of assets",
            )
            for asset in assets:
                self.assertEqual(
                    asset,
                    RESPONSE,
                    msg="Incorrect asset listed",
                )

            for a in mock_get.call_args_list:
                self.assertEqual(
                    tuple(a),
                    (
                        (f"url/{ROOT}/{SUBPATH}",),
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

    def test_assets_list_with_params(self):
        """
        Test asset listing
        """
        with mock.patch.object(self.arch.session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                assets=[
                    RESPONSE,
                ],
            )

            assets = list(
                self.arch.assets.list(
                    props={
                        "confirmation_status": "CONFIRMED",
                    },
                    attrs={"arc_firmware_version": "1.0"},
                )
            )
            self.assertEqual(
                len(assets),
                1,
                msg="incorrect number of assets",
            )
            for asset in assets:
                self.assertEqual(
                    asset,
                    RESPONSE,
                    msg="Incorrect asset listed",
                )

            for a in mock_get.call_args_list:
                self.assertEqual(
                    tuple(a),
                    (
                        ((f"url/{ROOT}/{SUBPATH}"),),
                        {
                            "headers": {
                                "authorization": "Bearer authauthauth",
                            },
                            "params": {
                                "confirmation_status": "CONFIRMED",
                                "attributes.arc_firmware_version": "1.0",
                            },
                            "verify": True,
                        },
                    ),
                    msg="GET method called incorrectly",
                )

    def test_assets_read_by_signature(self):
        """
        Test asset listing
        """
        with mock.patch.object(self.arch.session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                assets=[
                    RESPONSE,
                ],
            )

            asset = self.arch.assets.read_by_signature()
            self.assertEqual(
                asset,
                RESPONSE,
                msg="Incorrect asset listed",
            )

            self.assertEqual(
                tuple(mock_get.call_args),
                (
                    (f"url/{ROOT}/{SUBPATH}",),
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
