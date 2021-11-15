"""
Tests the upload and download functionality of the SDK
"""
from contextlib import suppress
from filecmp import clear_cache, cmp
from os import environ, remove
from time import sleep
from unittest import TestCase

from archivist.archivist import Archivist
from archivist.timestamp import now_timestamp


# pylint: disable=fixme
# pylint: disable=missing-docstring
# pylint: disable=unused-variable


class TestSBOM(TestCase):
    """
    Test Archivist SBOM upload/download
    """

    TEST_SBOM_PATH = "functests/test_resources/bom.xml"
    TEST_SBOM_DOWNLOAD_PATH = "functests/test_resources/downloaded_bom.xml"

    @classmethod
    def setUp(cls):
        with open(environ["TEST_AUTHTOKEN_FILENAME"], encoding="utf-8") as fd:
            auth = fd.read().strip()

        cls.arch = Archivist(environ["TEST_ARCHIVIST"], auth=auth, verify=False)
        cls.file_uuid: str = ""

        with suppress(FileNotFoundError):
            remove(cls.TEST_SBOM_DOWNLOAD_PATH)

    @classmethod
    def tearDown(cls) -> None:
        """Remove the downloaded sbom for subsequent test runs"""
        with suppress(FileNotFoundError):
            remove(cls.TEST_SBOM_DOWNLOAD_PATH)

    def test_sbom_upload_and_download(self):
        """
        Test sbom upload and download through the SDK
        """
        now = now_timestamp()
        with open(self.TEST_SBOM_PATH, "rb") as fd:
            metadata = self.arch.sboms.upload(fd)

        identity = metadata.identity
        with open(self.TEST_SBOM_DOWNLOAD_PATH, "wb") as fd:
            sbom = self.arch.sboms.download(identity, fd)

        clear_cache()
        self.assertTrue(
            cmp(self.TEST_SBOM_PATH, self.TEST_SBOM_DOWNLOAD_PATH, shallow=False)
        )

        metadata1 = self.arch.sboms.read(identity)
        self.assertEqual(
            metadata,
            metadata1,
            msg="Metadata not correct",
        )

        sleep(1)  # otherwise test fails
        metadatas = list(self.arch.sboms.list(metadata={"uploaded_since": now}))
        self.assertEqual(
            len(metadatas),
            1,
            msg="No. of SBOMS should be 1",
        )
        self.assertEqual(
            metadatas[0],
            metadata,
            msg="Metadata not correct",
        )
