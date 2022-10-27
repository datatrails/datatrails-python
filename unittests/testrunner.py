"""
Test runner
"""
from logging import getLogger
from os import environ
from unittest import TestCase

# from archivist.errors import ArchivistBadRequestError

# pylint: disable=missing-docstring
# pylint: disable=protected-access
# pylint: disable=unused-variable

from archivist.archivist import Archivist
from archivist.assets import Asset
from archivist.constants import ASSET_BEHAVIOURS
from archivist.logger import set_logger
from archivist.runner import tree

if "TEST_DEBUG" in environ and environ["TEST_DEBUG"]:
    set_logger(environ["TEST_DEBUG"])

LOGGER = getLogger(__name__)

ASSET_ID = "assets/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
ASSET_NAME = "radiation bag 1"
ASSETS_RESPONSE = {
    "attributes": {
        "arc_display_name": ASSET_NAME,
        "radioactive": True,
        "radiation_level": 0,
        "weight": 0,
    },
    "behaviours": ASSET_BEHAVIOURS,
    "confirmation_status": "CONFIRMED",
    "identity": ASSET_ID,
}

ASSETS_NO_NAME_RESPONSE = {
    "attributes": {
        "radioactive": True,
        "radiation_level": 0,
        "weight": 0,
    },
    "behaviours": ASSET_BEHAVIOURS,
    "confirmation_status": "CONFIRMED",
    "identity": ASSET_ID,
}


class TestRunner(TestCase):
    """
    Test Archivist Runner
    """

    maxDiff = None

    def setUp(self):
        self.arch = Archivist("url", "authauthauth")

    def tearDown(self):
        self.arch.close()

    def test_runner_str(self):
        """
        Test runner str
        """
        self.assertEqual(
            str(self.arch.runner),
            "Runner(url)",
            msg="Incorrect str",
        )

    def test_runner_asset_id(self):
        """
        Test runner asset_id
        """
        runner = self.arch.runner
        runner.entities = tree()
        runner.entities[ASSET_NAME] = Asset(**ASSETS_RESPONSE)
        self.assertEqual(
            runner.identity(ASSET_NAME),
            ASSET_ID,
            msg="Incorrect ID",
        )
        self.assertIsNone(
            runner.identity(ASSET_NAME + "garbage"),
            msg="Incorrect ID",
        )
