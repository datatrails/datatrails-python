"""
Tests the upload and download functionality of the SDK
"""
from contextlib import suppress
from filecmp import clear_cache, cmp
from io import BytesIO
from json import dumps as json_dumps
from os import getenv, remove
from unittest import skipIf

from archivist import logger
from archivist.archivist import Archivist
from archivist.errors import ArchivistBadRequestError
from archivist.utils import get_auth, get_url

from .constants import TestCase

if getenv("DATATRAILS_LOGLEVEL") is not None:
    logger.set_logger(getenv("DATATRAILS_LOGLEVEL"))

LOGGER = logger.LOGGER

# pylint: disable=fixme
# pylint: disable=missing-docstring
# pylint: disable=unused-variable


class TestAttachmentsCreate(TestCase):
    """
    Test Archivist Attachment Create method
    """

    DATATRAILS_DOCX_PATH = "functests/test_resources/loremipsum.docx"
    DATATRAILS_DOCX_DOWNLOAD_PATH = (
        "functests/test_resources/downloaded_loremipsum.docx"
    )
    DATATRAILS_IMAGE_PATH = "functests/test_resources/datatrails_logo.png"
    DATATRAILS_IMAGE_DOWNLOAD_PATH = "functests/test_resources/downloaded_image.jpg"

    def setUp(self):
        auth = get_auth(
            auth_token=getenv("DATATRAILS_AUTHTOKEN"),
            auth_token_filename=getenv("DATATRAILS_AUTHTOKEN_FILENAME"),
            client_id=getenv("DATATRAILS_APPREG_CLIENT"),
            client_secret=getenv("DATATRAILS_APPREG_SECRET"),
            client_secret_filename=getenv("DATATRAILS_APPREG_SECRET_FILENAME"),
        )
        self.arch = Archivist(getenv("DATATRAILS_URL"), auth)
        self.file_uuid: str = ""

        with suppress(FileNotFoundError):
            remove(self.DATATRAILS_IMAGE_DOWNLOAD_PATH)

        with suppress(FileNotFoundError):
            remove(self.DATATRAILS_DOCX_DOWNLOAD_PATH)

    def tearDown(self) -> None:
        """Remove the downloaded image for subsequent test runs"""
        self.arch.close()
        with suppress(FileNotFoundError):
            remove(self.DATATRAILS_IMAGE_DOWNLOAD_PATH)

        with suppress(FileNotFoundError):
            remove(self.DATATRAILS_DOCX_DOWNLOAD_PATH)

    def test_attachment_upload_and_download(self):
        """
        Test file upload through the SDK
        Test file download through the SDK
        """
        with open(self.DATATRAILS_IMAGE_PATH, "rb") as fd:
            attachment = self.arch.attachments.upload(fd)
            file_uuid = attachment["identity"]

        with open(self.DATATRAILS_IMAGE_DOWNLOAD_PATH, "wb") as fd:
            attachment = self.arch.attachments.download(file_uuid, fd)

        # Check the downloaded file is identical to the one that was uploaded
        clear_cache()
        self.assertTrue(
            cmp(
                self.DATATRAILS_IMAGE_PATH,
                self.DATATRAILS_IMAGE_DOWNLOAD_PATH,
                shallow=False,
            )
        )

    def test_attachment_upload_and_download_docx(self):
        """
        Test file upload through the SDK
        Test file download through the SDK
        """
        with open(self.DATATRAILS_DOCX_PATH, "rb") as fd:
            attachment = self.arch.attachments.upload(fd)
            file_uuid = attachment["identity"]

        LOGGER.debug("attachment %s", json_dumps(attachment, indent=4))

        self.assertEqual(
            attachment["mime_type"],
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            msg="UPLOAD incorrect mimetype",
        )

        with open(self.DATATRAILS_DOCX_DOWNLOAD_PATH, "wb") as fd:
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
        getenv("DATATRAILS_BLOB_IDENTITY") is None,
        "cannot run test as DATATRAILS_BLOB_IDENTITY is not set",
    )
    def test_attachment_info(self):
        """
        Test file info through the SDK
        Test file download through the SDK
        """
        file_uuid = getenv("DATATRAILS_BLOB_IDENTITY")
        info = self.arch.attachments.info(file_uuid)
        LOGGER.debug("attachment info %s", json_dumps(info, indent=4))

    def test_attachment_upload_and_download_allow_insecure(self):
        """
        Test file upload through the SDK
        Test file download through the SDK
        """
        with open(self.DATATRAILS_IMAGE_PATH, "rb") as fd:
            attachment = self.arch.attachments.upload(fd)
            file_uuid = attachment["identity"]

        with open(self.DATATRAILS_IMAGE_DOWNLOAD_PATH, "wb") as fd:
            attachment = self.arch.attachments.download(
                file_uuid, fd, params={"allow_insecure": "true"}
            )

        # Check the downloaded file is identical to the one that was uploaded
        clear_cache()
        self.assertTrue(
            cmp(
                self.DATATRAILS_IMAGE_PATH,
                self.DATATRAILS_IMAGE_DOWNLOAD_PATH,
                shallow=False,
            )
        )

    def test_attachment_upload_and_download_strict(self):
        """
        Test file upload through the SDK
        Test file download through the SDK
        """
        with open(self.DATATRAILS_IMAGE_PATH, "rb") as fd:
            attachment = self.arch.attachments.upload(fd)
            file_uuid = attachment["identity"]

        with open(self.DATATRAILS_IMAGE_DOWNLOAD_PATH, "wb") as fd, self.assertRaises(
            ArchivistBadRequestError
        ):
            attachment = self.arch.attachments.download(
                file_uuid, fd, params={"strict": "true"}
            )


class TestAttachmentstMalware(TestCase):
    """
    Test Archivist Attachment Create method
    """

    # we dont want to actually store these files in our repo so download
    # every time.
    DATATRAILS_MALWARE1 = "https://secure.eicar.org/eicar.com"
    DATATRAILS_MALWARE2 = "https://secure.eicar.org/eicar.com.txt"
    DATATRAILS_MALWARE3 = "https://secure.eicar.org/eicar.com.zip"
    DATATRAILS_MALWARE4 = "https://secure.eicar.org/eicarcom2.zip"

    @classmethod
    def setUpClass(cls):
        cls.malware1 = BytesIO()
        get_url(cls.DATATRAILS_MALWARE1, cls.malware1)

        cls.malware2 = BytesIO()
        get_url(cls.DATATRAILS_MALWARE2, cls.malware2)

        cls.malware3 = BytesIO()
        get_url(cls.DATATRAILS_MALWARE3, cls.malware3)

        cls.malware4 = BytesIO()
        get_url(cls.DATATRAILS_MALWARE4, cls.malware4)

    def setUp(self):
        auth = get_auth(
            auth_token=getenv("DATATRAILS_AUTHTOKEN"),
            auth_token_filename=getenv("DATATRAILS_AUTHTOKEN_FILENAME"),
            client_id=getenv("DATATRAILS_APPREG_CLIENT"),
            client_secret=getenv("DATATRAILS_APPREG_SECRET"),
            client_secret_filename=getenv("DATATRAILS_APPREG_SECRET_FILENAME"),
        )
        self.arch = Archivist(getenv("DATATRAILS_URL"), auth)

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
