"""
Test archivist
"""

from io import BytesIO
import json
from unittest import TestCase, mock

from archivist.archivist import Archivist
from archivist.constants import ROOT, ATTACHMENTS_SUBPATH, ATTACHMENTS_LABEL

from .mock_response import MockResponse

# pylint: disable=protected-access


PROPS = {
    "hash": {"alg": "SHA256", "value": "xxxxxxxxxxxxxxxxxxxxxxx"},
    "mime_type": "image/jpeg",
    "timestamp_accepted": "2019-11-07T15:31:49Z",
    "size": 31424,
}
IDENTITY = f"{ATTACHMENTS_LABEL}/xxxxxxxx"
SUBPATH = f"{ATTACHMENTS_SUBPATH}/{ATTACHMENTS_LABEL}"

RESPONSE = {
    **PROPS,
    "identity": IDENTITY,
}
REQUEST_DATA = json.dumps(PROPS)


class TestAttachments(TestCase):
    """
    Test Archivist Attachments Create method
    """

    maxDiff = None

    def setUp(self):
        self.arch = Archivist("url", "authauthauth")
        self.mockstream = BytesIO(b"somelongstring")

    def test_attachments_str(self):
        """
        Test attachments str
        """
        self.assertEqual(
            str(self.arch.attachments),
            "AttachmentsClient(url)",
            msg="Incorrect str",
        )

    def test_attachments_upload(self):
        """
        Test attachment upload
        """
        with mock.patch.object(self.arch._session, "post") as mock_post:
            mock_post.return_value = MockResponse(200, **RESPONSE)

            attachment = self.arch.attachments.upload(self.mockstream)
            args, kwargs = mock_post.call_args
            self.assertEqual(
                args,
                (f"url/{ROOT}/{SUBPATH}",),
                msg="UPLOAD method called incorrectly",
            )
            self.assertTrue(
                "headers" in kwargs,
                msg="UPLOAD no headers found",
            )
            headers = kwargs["headers"]
            self.assertTrue(
                "authorization" in headers,
                msg="UPLOAD no authorization found",
            )
            self.assertEqual(
                headers["authorization"],
                "Bearer authauthauth",
                msg="UPLOAD incorrect authorization",
            )
            self.assertTrue(
                headers["content-type"].startswith("multipart/form-data;"),
                msg="UPLOAD incorrect content-type",
            )
            self.assertTrue(
                kwargs["verify"],
                msg="UPLOAD method called incorrectly",
            )
            self.assertTrue(
                "data" in kwargs,
                msg="UPLOAD no data found",
            )
            fields = kwargs["data"].fields
            self.assertTrue(
                "file" in fields,
                msg="UPLOAD no file found",
            )
            self.assertEqual(
                fields["file"][0],
                "filename",
                msg="UPLOAD incorrect filename",
            )
            self.assertEqual(
                fields["file"][2],
                "image/jpg",
                msg="UPLOAD incorrect filetype",
            )
            self.assertEqual(
                attachment,
                RESPONSE,
                msg="UPLOAD method called incorrectly",
            )

    def test_attachments_download(self):
        """
        Test attachment download
        """

        with mock.patch.object(self.arch._session, "get") as mock_get:

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
                attachment = self.arch.attachments.download(IDENTITY, fd)
                args, kwargs = mock_get.call_args
                self.assertEqual(
                    args,
                    (f"url/{ROOT}/{ATTACHMENTS_SUBPATH}/{IDENTITY}",),
                    msg="DOWNLOAD method called incorrectly",
                )
                self.assertEqual(
                    kwargs,
                    {
                        "headers": {
                            "authorization": "Bearer authauthauth",
                            "content-type": "application/json",
                        },
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

    def test_attachments_download_with_query(self):
        """
        Test attachment download - usually both allow options are
        not required.
        """

        with mock.patch.object(self.arch._session, "get") as mock_get:

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
                attachment = self.arch.attachments.download(
                    IDENTITY,
                    fd,
                    query={"allow_insecure": True, "allow_not_scanned": True},
                )
                args, kwargs = mock_get.call_args
                self.assertEqual(
                    args,
                    (
                        f"url/{ROOT}/{ATTACHMENTS_SUBPATH}/{IDENTITY}"
                        "?allow_insecure=True&allow_not_scanned=True",
                    ),
                    msg="DOWNLOAD method called incorrectly",
                )
                self.assertEqual(
                    kwargs,
                    {
                        "headers": {
                            "authorization": "Bearer authauthauth",
                            "content-type": "application/json",
                        },
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
