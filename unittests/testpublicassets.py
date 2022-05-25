"""
Test archivist
"""

from logging import getLogger
from os import environ
from unittest import TestCase

from archivist.archivist import Archivist
from archivist.logger import set_logger

# pylint: disable=missing-docstring
# pylint: disable=protected-access
# pylint: disable=unused-variable

if "TEST_DEBUG" in environ and environ["TEST_DEBUG"]:
    set_logger(environ["TEST_DEBUG"])

LOGGER = getLogger(__name__)


class TestPublicAssetsBase(TestCase):
    """
    Test Archivist Assets Base
    """

    maxDiff = None

    def setUp(self):
        self.arch = Archivist("url", None, max_time=1)

    def tearDown(self):
        self.arch = None


class TestPublicAssetsUtil(TestPublicAssetsBase):
    """
    Test Archivist Public Assets utility
    """

    def test_public_assets_str(self):
        """
        Test assets str
        """
        self.assertEqual(
            str(self.arch.publicassets),
            "PublicAssetsClient(url)",
            msg="Incorrect str",
        )
