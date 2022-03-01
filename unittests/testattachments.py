"""
Test archivist
"""

from io import BytesIO
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
CREATE_RESULT = {
    "arc_attachment_identity": IDENTITY,
    "arc_hash_alg": "SHA256",
    "arc_hash_value": "xxxxxxxxxxxxxxxxxxxxxxx",
}


class TestAttachmentsBase(TestCase):
    """
    Test Archivist Attachments Create method
    """

    maxDiff = None

    def setUp(self):
        self.arch = Archivist("url", "authauthauth")

    def test_attachments_str(self):
        """
        Test attachments str
        """
        self.assertEqual(
            str(self.arch.attachments),
            "AttachmentsClient(url)",
            msg="Incorrect str",
        )


# A bug in the python mock_open helper function prevents the successful
# unittesting of the create method as it does not return an iterable for
# binary data. This is fixed in 3.8.
#
# Pro tem, leave this code commented out and add a pragma: no cover to
# the create method in the attachments client.
#
# def mock_open(read_data=''):
#  """
#  Note: the special unittest mock_open still does not return an iterable as
#  originally reported in 2014 and still not fixed. So we have to add
#  an iterable ourselves. (finding this out wasted 4 hours ...)
#
#  Fixed in 3.8 but not backported
#
#  https://bugs.python.org/issue32933
#  https://bugs.python.org/issue21258
#
# The following does not have any affect... (as found on stack overflow)
# Many variations on the code below were tried.
#  """
#  f_open = mock.mock_open(read_data=read_data)
#  f_open.return_value.__iter__ = lambda self: self
#  f_open.return_value.__next__ = lambda self: next(iter(self.readline, ''))
#  return f_open
#
#
# class TestAttachmentsCreate(TestAttachmentsBase):
#    """
#    Test Archivist Attachments Create method
#    """
#
#    maxDiff = None
#
#    def test_attachments_create(self):
#        """
#        Test attachment create
#        """
#        with mock.patch.object(self.arch._session, "post") as mock_post, mock.patch(
#            "archivist.attachments.open",
#            mock_open(read_data="a long string"),
#        ) as mocked_open:
#            mock_post.return_value = MockResponse(200, **RESPONSE)
#
#            result = self.arch.attachments.create(
#                {
#                    "filename": "test_filename",
#                    "content_type": "image/jpg",
#                },
#            )
#            self.assertEqual(
#                result,
#                CREATE_RESULT,
#                msg="CREATE method called incorrectly",
#            )
#            args, _ = mocked_open.call_args
#            self.assertEqual(
#                args,
#                (
#                    "test_filename",
#                    "rb",
#                ),
#                msg="os_open method called incorrectly",
#            )
#
#            args, kwargs = mock_post.call_args
#            self.assertEqual(
#                args,
#                (f"url/{ROOT}/{SUBPATH}",),
#                msg="UPLOAD method called incorrectly",
#            )
#            self.assertEqual(
#                "headers" in kwargs,
#                True,
#                msg="UPLOAD no headers found",
#            )


class TestAttachmentsUpload(TestAttachmentsBase):
    """
    Test Archivist Attachments Upload method
    """

    maxDiff = None

    def setUp(self):
        super().setUp()
        self.mockstream = BytesIO(b"somelongstring")

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
            self.assertEqual(
                "headers" in kwargs,
                True,
                msg="UPLOAD no headers found",
            )
            headers = kwargs["headers"]
            self.assertEqual(
                "authorization" in headers,
                True,
                msg="UPLOAD no authorization found",
            )
            self.assertEqual(
                headers["authorization"],
                "Bearer authauthauth",
                msg="UPLOAD incorrect authorization",
            )
            self.assertEqual(
                headers["content-type"].startswith("multipart/form-data;"),
                True,
                msg="UPLOAD incorrect content-type",
            )
            self.assertEqual(
                kwargs["verify"],
                True,
                msg="UPLOAD method called incorrectly",
            )
            self.assertEqual(
                "data" in kwargs,
                True,
                msg="UPLOAD no data found",
            )
            fields = kwargs["data"].fields
            self.assertEqual(
                "file" in fields,
                True,
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


class TestAttachmentsDownload(TestAttachmentsBase):
    """
    Test Archivist Attachments Downloads method
    """

    maxDiff = None

    def common_attachments_download(self, input_params, expected_params):
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
                attachment = self.arch.attachments.download(
                    IDENTITY,
                    fd,
                    params=input_params,
                )
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
                        },
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

    def test_attachments_download(self):
        """
        Test attachment download
        """

        self.common_attachments_download(None, {})

    def test_attachments_download_with_allow_insecure(self):
        """
        Test attachment download with allow_insecure
        """

        self.common_attachments_download(
            {"allow_insecure": "true"},
            {"allow_insecure": "true"},
        )

    def test_attachments_download_with_strict(self):
        """
        Test attachment download with strict
        """

        self.common_attachments_download(
            {"strict": "true"},
            {"strict": "true"},
        )
