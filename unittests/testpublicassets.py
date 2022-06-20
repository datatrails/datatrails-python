"""
Test archivist
"""

from logging import getLogger
from os import environ
from unittest import TestCase

from archivist.archivistpublic import ArchivistPublic
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
        self.public = ArchivistPublic(max_time=1)

    def tearDown(self):
        self.public.close()
        self.public = None


class TestPublicAssetsUtil(TestPublicAssetsBase):
    """
    Test Archivist Public Assets utility
    """

    def test_public_assets_str(self):
        """
        Test assets str
        """
        self.assertEqual(
            str(self.public.assets),
            "AssetsPublic()",
            msg="Incorrect str",
        )
