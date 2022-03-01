"""
Test runner
"""
from logging import getLogger
from os import environ
from unittest import TestCase

from archivist.errors import ArchivistInvalidOperationError

# pylint: disable=missing-docstring
# pylint: disable=protected-access
# pylint: disable=unused-variable

from archivist.archivist import Archivist
from archivist.runner import _ActionMap
from archivist.logger import set_logger

if "TEST_DEBUG" in environ and environ["TEST_DEBUG"]:
    set_logger(environ["TEST_DEBUG"])

LOGGER = getLogger(__name__)


class TestRunnerActionMap(TestCase):
    """
    Test Archivist Runner
    """

    maxDiff = None

    def setUp(self):
        self.arch = Archivist("url", "authauthauth")
        self.actionmap = _ActionMap(self.arch)

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
