"""
Tests the upload and download functionality of the SDK
"""
from contextlib import suppress
from filecmp import clear_cache, cmp
from json import dumps as json_dumps
from io import BytesIO
from os import getenv, remove
from unittest import skipIf

from archivist.archivist import Archivist
from archivist.errors import ArchivistBadRequestError
from archivist.utils import get_auth, get_url

from archivist import logger

from .constants import TestCase

if getenv("RKVST_LOGLEVEL") is not None:
    logger.set_logger(getenv("RKVST_LOGLEVEL"))

LOGGER = logger.LOGGER

# pylint: disable=fixme
# pylint: disable=missing-docstring
# pylint: disable=unused-variable


class TestAttachmentsCreate(TestCase):
    """
    Test Archivist Attachment Create method
    """

    RKVST_DOCX_PATH = "functests/test_resources/loremipsum.docx"
    RKVST_DOCX_DOWNLOAD_PATH = "functests/test_resources/downloaded_loremipsum.docx"
    RKVST_IMAGE_PATH = "functests/test_resources/rkvst_logo.png"
    RKVST_IMAGE_DOWNLOAD_PATH = "functests/test_resources/downloaded_image.jpg"

    def setUp(self):
        auth = get_auth(
            auth_token=getenv("RKVST_AUTHTOKEN"),
            auth_token_filename=getenv("RKVST_AUTHTOKEN_FILENAME"),
            client_id=getenv("RKVST_APPREG_CLIENT"),
            client_secret=getenv("RKVST_APPREG_SECRET"),
            client_secret_filename=getenv("RKVST_APPREG_SECRET_FILENAME"),
        )
        self.arch = Archivist(getenv("RKVST_URL"), auth)
        self.file_uuid: str = ""

        with suppress(FileNotFoundError):
            remove(self.RKVST_IMAGE_DOWNLOAD_PATH)

        with suppress(FileNotFoundError):
            remove(self.RKVST_DOCX_DOWNLOAD_PATH)

    def tearDown(self) -> None:
        """Remove the downloaded image for subsequent test runs"""
        self.arch.close()
        with suppress(FileNotFoundError):
            remove(self.RKVST_IMAGE_DOWNLOAD_PATH)

        with suppress(FileNotFoundError):
            remove(self.RKVST_DOCX_DOWNLOAD_PATH)

    def test_attachment_upload_and_download(self):
        """
        Test file upload through the SDK
        Test file download through the SDK
        """
        with open(self.RKVST_IMAGE_PATH, "rb") as fd:
            attachment = self.arch.attachments.upload(fd)
            file_uuid = attachment["identity"]

        with open(self.RKVST_IMAGE_DOWNLOAD_PATH, "wb") as fd:
            attachment = self.arch.attachments.download(file_uuid, fd)

        # Check the downloaded file is identical to the one that was uploaded
        clear_cache()
        self.assertTrue(
            cmp(self.RKVST_IMAGE_PATH, self.RKVST_IMAGE_DOWNLOAD_PATH, shallow=False)
        )

    def test_attachment_upload_and_download_docx(self):
        """
        Test file upload through the SDK
        Test file download through the SDK
        """
        with open(self.RKVST_DOCX_PATH, "rb") as fd:
            attachment = self.arch.attachments.upload(fd)
            file_uuid = attachment["identity"]

        LOGGER.debug("attachment %s", json_dumps(attachment, indent=4))

        self.assertEqual(
            attachment["mime_type"],
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            msg="UPLOAD incorrect mimetype",
        )

        with open(self.RKVST_DOCX_DOWNLOAD_PATH, "wb") as fd:
            attachment = self.arch.attachments.download(file_uuid, fd)

        LOGGER.debug("attachment %s", attachment.headers)
        self.assertEqual(
            attachment.headers["content-type"],
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            msg="UPLOAD incorrect mimetype",
        )

        info = self.arch.attachments.info(file_uuid)
        self.assertEqual(
            info["mime_type"],
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            msg="UPLOAD incorrect mimetype",
        )

    @skipIf(
        getenv("RKVST_BLOB_IDENTITY") is None,
        "cannot run test as RKVST_BLOB_IDENTITY is not set",
    )
    def test_attachment_info(self):
        """
        Test file info through the SDK
        Test file download through the SDK
        """
        file_uuid = getenv("RKVST_BLOB_IDENTITY")
        info = self.arch.attachments.info(file_uuid)
        LOGGER.debug("attachment info %s", json_dumps(info, indent=4))

    def test_attachment_upload_and_download_allow_insecure(self):
        """
        Test file upload through the SDK
        Test file download through the SDK
        """
        with open(self.RKVST_IMAGE_PATH, "rb") as fd:
            attachment = self.arch.attachments.upload(fd)
            file_uuid = attachment["identity"]

        with open(self.RKVST_IMAGE_DOWNLOAD_PATH, "wb") as fd:
            attachment = self.arch.attachments.download(
                file_uuid, fd, params={"allow_insecure": "true"}
            )

        # Check the downloaded file is identical to the one that was uploaded
        clear_cache()
        self.assertTrue(
            cmp(self.RKVST_IMAGE_PATH, self.RKVST_IMAGE_DOWNLOAD_PATH, shallow=False)
        )

    def test_attachment_upload_and_download_strict(self):
        """
        Test file upload through the SDK
        Test file download through the SDK
        """
        with open(self.RKVST_IMAGE_PATH, "rb") as fd:
            attachment = self.arch.attachments.upload(fd)
            file_uuid = attachment["identity"]

        with open(self.RKVST_IMAGE_DOWNLOAD_PATH, "wb") as fd:
            with self.assertRaises(ArchivistBadRequestError):
                attachment = self.arch.attachments.download(
                    file_uuid, fd, params={"strict": "true"}
                )


class TestAttachmentstMalware(TestCase):
    """
    Test Archivist Attachment Create method
    """

    # we dont want to actually store these files in our repo so download
    # every time.
    RKVST_MALWARE1 = "https://secure.eicar.org/eicar.com"
    RKVST_MALWARE2 = "https://secure.eicar.org/eicar.com.txt"
    RKVST_MALWARE3 = "https://secure.eicar.org/eicar.com.zip"
    RKVST_MALWARE4 = "https://secure.eicar.org/eicarcom2.zip"

    @classmethod
    def setUpClass(cls):
        cls.malware1 = BytesIO()
        get_url(cls.RKVST_MALWARE1, cls.malware1)

        cls.malware2 = BytesIO()
        get_url(cls.RKVST_MALWARE2, cls.malware2)

        cls.malware3 = BytesIO()
        get_url(cls.RKVST_MALWARE3, cls.malware3)

        cls.malware4 = BytesIO()
        get_url(cls.RKVST_MALWARE4, cls.malware4)

    def setUp(self):
        auth = get_auth(
            auth_token_filename=getenv("RKVST_AUTHTOKEN_FILENAME"),
            client_id=getenv("RKVST_APPREG_CLIENT"),
            client_secret_filename=getenv("RKVST_APPREG_SECRET_FILENAME"),
        )
        self.arch = Archivist(getenv("RKVST_URL"), auth)

    def tearDown(self):
        self.arch.close()

    def test_attachment_malware_scan1(self):
        """
        Test file upload through the SDK
        """
        attachment = self.arch.attachments.upload(self.malware1)
        LOGGER.debug("attachment %s", json_dumps(attachment, indent=4))
        response = self.arch.attachments.info(attachment["identity"])
        LOGGER.debug("response %s", json_dumps(response, indent=4))

    def test_attachment_malware_scan2(self):
        """
        Test file upload through the SDK
        """
        attachment = self.arch.attachments.upload(self.malware2)
        LOGGER.debug("attachment %s", json_dumps(attachment, indent=4))
        response = self.arch.attachments.info(attachment["identity"])
        LOGGER.debug("response %s", json_dumps(response, indent=4))

    def test_attachment_malware_scan3(self):
        """
        Test file upload through the SDK
        """
        attachment = self.arch.attachments.upload(self.malware3)
        LOGGER.debug("attachment %s", json_dumps(attachment, indent=4))
        response = self.arch.attachments.info(attachment["identity"])
        LOGGER.debug("response %s", json_dumps(response, indent=4))

    def test_attachment_malware_scan4(self):
        """
        Test file upload through the SDK
        """
        attachment = self.arch.attachments.upload(self.malware4)
        LOGGER.debug("attachment %s", json_dumps(attachment, indent=4))
        response = self.arch.attachments.info(attachment["identity"])
        LOGGER.debug("response %s", json_dumps(response, indent=4))
