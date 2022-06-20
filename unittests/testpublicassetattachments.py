"""
Test archivist
"""

from io import BytesIO
from logging import getLogger
from os import environ
from unittest import TestCase, mock

from archivist.archivistpublic import ArchivistPublic
from archivist.constants import (
    ROOT,
    ASSETS_LABEL,
    ATTACHMENTS_LABEL,
    ASSETATTACHMENTS_LABEL,
    ASSETATTACHMENTS_SUBPATH,
)
from archivist.logger import set_logger

from .mock_response import MockResponse

# pylint: disable=protected-access

if "TEST_DEBUG" in environ and environ["TEST_DEBUG"]:
    set_logger(environ["TEST_DEBUG"])

LOGGER = getLogger(__name__)

PROPS = {
    "hash": {"alg": "SHA256", "value": "xxxxxxxxxxxxxxxxxxxxxxx"},
    "mime_type": "image/jpeg",
    "timestamp_accepted": "2019-11-07T15:31:49Z",
    "size": 31424,
}
URL = "https://app.rkvst.io"
ASSET_UUID = "b2678528-0136-4876-ad56-904e12c4b4c6"
ASSET_ID = f"{URL}/{ROOT}/public{ASSETS_LABEL}/{ASSET_UUID}"
ATTACHMENT_UUID = "abcdef28-0136-4876-ad56-904e12c4b4c6"
ATTACHMENT_ID = f"{ATTACHMENTS_LABEL}/{ATTACHMENT_UUID}"
SUBPATH = (
    f"{ASSETATTACHMENTS_SUBPATH}/{ASSETATTACHMENTS_LABEL}/"
    f"public{ASSETS_LABEL}/{ASSET_UUID}/{ATTACHMENT_UUID}"
)
LOGGER.debug("Subpath %s", SUBPATH)
RESPONSE = {
    **PROPS,
    "identity": ATTACHMENT_ID,
}
INFO = {
    "hash": {
        "alg": "SHA256",
        "value": "e1105070ba828007508566e28a2b8d4c65d192e9eaf3b7868382b7cae747b397",
    },
    "identity": ATTACHMENT_ID,
    "issuer": "",
    "mime_type": "application/zip",
    "size": 308,
    "subject": "",
    "tenantid": "",
    "timestamp_accepted": "2022-03-01T09:25:43Z",
    "scanned_status": "NOT_SCANNED",
    "scanned_bad_reason": "",
    "scanned_timestamp": "",
}


class TestPublicAssetAttachmentsBase(TestCase):
    """
    Test Archivist Attachments Create method
    """

    maxDiff = None

    def setUp(self):
        self.public = ArchivistPublic()

    def tearDown(self):
        self.public.close()

    def test_assetattachments_str(self):
        """
        Test attachments str
        """
        self.assertEqual(
            str(self.public.assetattachments),
            "AssetAttachmentsClient()",
            msg="Incorrect str",
        )


class TestPublicAssetAttachmentsDownload(TestPublicAssetAttachmentsBase):
    """
    Test Archivist Attachments Downloads method
    """

    maxDiff = None

    def common_assetattachments_download(
        self,
        input_params,
        expected_params,
    ):
        """
        Test attachment download
        """

        with mock.patch.object(self.public.session, "get") as mock_get:

            def iter_content():
                i = 0

                def filedata(chunk_size=4096):  # pylint: disable=unused-argument
                    nonlocal i
                    while i < 4:
                        i += 1

                        if i == 2:
                            yield None

                        yield b"chunkofbytes"

                return filedata

            mock_get.return_value = MockResponse(
                200,
                iter_content=iter_content(),
                **RESPONSE,
            )
            with BytesIO() as fd:
                attachment = self.public.assetattachments.download(
                    ASSET_ID,
                    ATTACHMENT_ID,
                    fd,
                    params=input_params,
                )
                args, kwargs = mock_get.call_args
                self.assertEqual(
                    args,
                    (f"{URL}/{ROOT}/{SUBPATH}",),
                    msg="DOWNLOAD method called incorrectly",
                )
                self.assertEqual(
                    kwargs,
                    {
                        "headers": {},
                        "params": expected_params,
                        "stream": True,
                        "verify": True,
                    },
                    msg="DOWNLOAD method called incorrectly",
                )
                self.assertEqual(
                    attachment,
                    RESPONSE,
                    msg="DOWNLOAD method called incorrectly",
                )

    def test_assetattachments_download(self):
        """
        Test attachment download
        """

        self.common_assetattachments_download(None, {})

    def test_assetattachments_download_with_allow_insecure(self):
        """
        Test attachment download with allow_insecure
        """

        self.common_assetattachments_download(
            {"allow_insecure": "true"},
            {"allow_insecure": "true"},
        )

    def test_assetattachments_download_with_strict(self):
        """
        Test attachment download with strict
        """

        self.common_assetattachments_download(
            {"strict": "true"},
            {"strict": "true"},
        )


class TestPublicAssetAttachmentsInfo(TestPublicAssetAttachmentsBase):
    """
    Test Archivist Attachments Info method
    """

    maxDiff = None

    def test_assetattachments_info(self):
        """
        Test attachment info
        """

        with mock.patch.object(self.public.session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                **INFO,
            )
            info = self.public.assetattachments.info(ASSET_ID, ATTACHMENT_ID)
            args, kwargs = mock_get.call_args
            self.assertEqual(
                args,
                (f"{URL}/{ROOT}/{SUBPATH}/info",),
                msg="INFO method called incorrectly",
            )
            self.assertEqual(
                kwargs,
                {
                    "headers": {},
                    "params": None,
                    "verify": True,
                },
                msg="INFO method called incorrectly",
            )
            self.assertEqual(
                info,
                INFO,
                msg="INFO method called incorrectly",
            )
