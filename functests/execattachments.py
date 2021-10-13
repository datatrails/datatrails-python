"""
Tests the upload and download functionality of the SDK
"""
import os
from os import environ
from unittest import TestCase
from contextlib import suppress
from filecmp import cmp

from archivist.archivist import Archivist


# pylint: disable=fixme
# pylint: disable=missing-docstring
# pylint: disable=unused-variable


class TestAssetCreate(TestCase):
    """
    Test Archivist Asset Create method
    """

    TEST_IMAGE_PATH = "functests/test_resources/Jitsuin_Logo_RGB.jpg"
    TEST_IMAGE_DOWNLOAD_PATH = "functests/test_resources/downloaded_image.jpg"

    @classmethod
    def setUp(cls):
        with open(environ["TEST_AUTHTOKEN_FILENAME"], encoding="utf-8") as fd:
            auth = fd.read().strip()
        cls.arch = Archivist(environ["TEST_ARCHIVIST"], auth=auth, verify=False)
        cls.file_uuid: str = ""

        with suppress(FileNotFoundError):
            os.remove(cls.TEST_IMAGE_DOWNLOAD_PATH)

    @classmethod
    def tearDown(cls) -> None:
        """Remove the downloaded image for subsequent test runs"""
        with suppress(FileNotFoundError):
            os.remove(cls.TEST_IMAGE_DOWNLOAD_PATH)

    def testfile_upload_and_download(self):
        """
        Test file upload through the SDK
        Test file download through the SDK
        """
        with open(self.TEST_IMAGE_PATH, "rb") as image:
            attachment = self.arch.attachments.upload(image)
            file_uuid = attachment["identity"]

        with open(self.TEST_IMAGE_DOWNLOAD_PATH, "wb") as image:
            attachment = self.arch.attachments.download(file_uuid, image)

        # Check the downloaded file is identical to the one that was uploaded
        self.assertTrue(
            cmp(self.TEST_IMAGE_PATH, self.TEST_IMAGE_DOWNLOAD_PATH, shallow=False)
        )
