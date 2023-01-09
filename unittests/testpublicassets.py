"""
Test public assets
"""

from logging import getLogger
from os import environ
from unittest import TestCase

from archivist.archivistpublic import ArchivistPublic
from archivist.logger import set_logger

# pylint: disable=missing-docstring
# pylint: disable=protected-access
# pylint: disable=unused-variable

if "RKVST_DEBUG" in environ and environ["RKVST_DEBUG"]:
    set_logger(environ["RKVST_DEBUG"])

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
