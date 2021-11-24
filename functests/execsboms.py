"""
Tests the upload and download functionality of the SDK
"""
from contextlib import suppress
from filecmp import clear_cache, cmp
from json import dumps as json_dumps
from os import environ, remove
from time import sleep
from unittest import TestCase

from archivist.archivist import Archivist
from archivist.logger import set_logger
from archivist.timestamp import now_timestamp


# pylint: disable=fixme
# pylint: disable=missing-docstring
# pylint: disable=unused-variable

if "TEST_DEBUG" in environ and environ["TEST_DEBUG"]:
    set_logger(environ["TEST_DEBUG"])


class TestSBOM(TestCase):
    """
    Test Archivist SBOM upload/download
    """

    maxDiff = None

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

        print("metadata", json_dumps(metadata.dict(), indent=4))
        identity = metadata.identity
        with open(self.TEST_SBOM_DOWNLOAD_PATH, "wb") as fd:
            sbom = self.arch.sboms.download(identity, fd)

        print("sbom", sbom)
        clear_cache()
        self.assertTrue(
            cmp(self.TEST_SBOM_PATH, self.TEST_SBOM_DOWNLOAD_PATH, shallow=False)
        )

        metadata1 = self.arch.sboms.read(identity)
        print("metadata1", json_dumps(metadata1.dict(), indent=4))
        self.assertEqual(
            metadata,
            metadata1,
            msg="Metadata not correct",
        )

        sleep(1)  # otherwise test fails
        metadatas = list(self.arch.sboms.list(metadata={"uploaded_since": now}))
        for i, m in enumerate(metadatas):
            print(i, ":", json_dumps(m.dict(), indent=4))

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

        sleep(1)  # otherwise test fails
        metadata2 = self.arch.sboms.publish(identity)
        print("metadata2", json_dumps(metadata2.dict(), indent=4))
        self.assertNotEqual(
            metadata1.published_date,
            metadata2.published_date,
            msg="Published_date not correct",
        )
        metadata3 = self.arch.sboms.publish(identity)
        print("metadata3", json_dumps(metadata3.dict(), indent=4))
        self.assertEqual(
            metadata2.published_date,
            metadata3.published_date,
            msg="Published_date not correct",
        )

        sleep(1)  # otherwise test fails
        metadata4 = self.arch.sboms.withdraw(identity)
        print("metadata4", json_dumps(metadata4.dict(), indent=4))
        self.assertNotEqual(
            metadata3.withdrawn_date,
            metadata4.withdrawn_date,
            msg="Withdrawn_date not correct",
        )
        self.assertEqual(
            metadata2.published_date,
            metadata4.published_date,
            msg="Published_date not correct",
        )

        metadata5 = self.arch.sboms.withdraw(identity)
        print("metadata5", json_dumps(metadata5.dict(), indent=4))
        self.assertEqual(
            metadata4.withdrawn_date,
            metadata5.withdrawn_date,
            msg="Withdrawn_date not correct",
        )

        sleep(1)  # otherwise test fails
        metadatas = list(
            self.arch.sboms.list(
                page_size=50,
                metadata={
                    "search": "*",
                    "privacy": "PUBLIC",
                },
            )
        )
        for i, m in enumerate(metadatas):
            print(i, ":", json_dumps(m.dict(), indent=4))
