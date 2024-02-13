"""
Test runner actionmap
"""

from logging import getLogger
from os import environ
from unittest import TestCase

# pylint: disable=missing-docstring
# pylint: disable=protected-access
# pylint: disable=unused-variable
from archivist.archivist import Archivist
from archivist.errors import ArchivistInvalidOperationError
from archivist.logger import set_logger
from archivist.runner import _ActionMap

if "DATATRAILS_LOGLEVEL" in environ and environ["DATATRAILS_LOGLEVEL"]:
    set_logger(environ["DATATRAILS_LOGLEVEL"])

LOGGER = getLogger(__name__)


class TestRunnerActionMap(TestCase):
    """
    Test Archivist Runner
    """

    maxDiff = None

    def setUp(self):
        self.arch = Archivist("url", "authauthauth")
        self.actionmap = _ActionMap(self.arch)

    def tearDown(self):
        self.arch.close()

    def test_runner_actionmap_action(self):
        """
        Test runner action map
        """
        self.assertEqual(
            self.actionmap.action("ASSETS_CREATE"),
            self.arch.assets.create_from_data,
            msg="Incorrect assets create method",
        )

    def test_runner_actionmap_illegal_action(self):
        """
        Test runner action map
        """
        with self.assertRaises(ArchivistInvalidOperationError):
            _ = self.actionmap.action("ASSETSS_CREATE")
