"""
Test archivist
"""

from io import BytesIO
from unittest import TestCase, mock

from archivist.archivist import Archivist
from archivist.constants import (
    ROOT,
    ASSETS_SUBPATH,
    ASSETS_LABEL,
    EVENTS_LABEL,
    ATTACHMENTS_SUBPATH,
    ATTACHMENTS_LABEL,
    ATTACHMENTS_ASSETS_EVENTS_LABEL,
)

from .mock_response import MockResponse

# pylint: disable=protected-access


PROPS = {
    "hash": {"alg": "SHA256", "value": "xxxxxxxxxxxxxxxxxxxxxxx"},
    "mime_type": "image/jpeg",
    "timestamp_accepted": "2019-11-07T15:31:49Z",
    "size": 31424,
}
UUID = "b2678528-0136-4876-ad56-904e12c4b4c6"
IDENTITY = f"{ATTACHMENTS_LABEL}/{UUID}"
SUBPATH = f"{ATTACHMENTS_SUBPATH}/{ATTACHMENTS_LABEL}"
ASSET_OR_EVENT_ID = f"{ASSETS_LABEL}/xxxx/{EVENTS_LABEL}/yyyy"
RESPONSE = {
    **PROPS,
    "identity": IDENTITY,
}
CREATE_RESULT = {
    "arc_attachment_identity": IDENTITY,
    "arc_hash_alg": "SHA256",
    "arc_hash_value": "xxxxxxxxxxxxxxxxxxxxxxx",
}

INFO = {
    "hash": {
        "alg": "SHA256",
        "value": "e1105070ba828007508566e28a2b8d4c65d192e9eaf3b7868382b7cae747b397",
    },
    "identity": IDENTITY,
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


# NB: Also applies to sboms.create() which has pragma no cover set as well...
#
# A bug in the python mock_open helper function prevents the successful
# unittesting of the create method as it does not return an iterable for
# binary data. This is fixed in 3.8.
#
# Pro tem, leave this code commented out and add a pragma: no cover to
# the create method in the attachments client.
#
# def mock_open(read_data=""):
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
#  f_open.return_value.__next__ = lambda self: next(iter(self.readline, ""))
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

    def common_attachments_download(
        self, input_params, expected_params, asset_or_event_id=None
    ):
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
                    asset_or_event_id=asset_or_event_id,
                )
                if asset_or_event_id is None:
                    arg1 = f"url/{ROOT}/{ATTACHMENTS_SUBPATH}/{IDENTITY}"
                else:
                    arg1 = (
                        f"url/{ROOT}/{ASSETS_SUBPATH}/{ATTACHMENTS_ASSETS_EVENTS_LABEL}"
                        f"/{asset_or_event_id}/{UUID}"
                    )

                args, kwargs = mock_get.call_args
                self.assertEqual(
                    args,
                    (arg1,),
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

    def test_attachments_download_with_asset_id(self):
        """
        Test attachment download
        """

        self.common_attachments_download(None, {}, asset_or_event_id=ASSET_OR_EVENT_ID)

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


class TestAttachmentsInfo(TestAttachmentsBase):
    """
    Test Archivist Attachments Info method
    """

    maxDiff = None

    def test_attachments_info(self):
        """
        Test attachment info
        """

        with mock.patch.object(self.arch._session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                **INFO,
            )
            info = self.arch.attachments.info(IDENTITY)
            args, kwargs = mock_get.call_args
            self.assertEqual(
                args,
                (f"url/{ROOT}/{ATTACHMENTS_SUBPATH}/{IDENTITY}/info",),
                msg="INFO method called incorrectly",
            )
            self.assertEqual(
                kwargs,
                {
                    "headers": {
                        "authorization": "Bearer authauthauth",
                    },
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

    def test_attachments_info_with_asset_id(self):
        """
        Test attachment info
        """

        with mock.patch.object(self.arch._session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                **INFO,
            )
            info = self.arch.attachments.info(
                IDENTITY, asset_or_event_id=ASSET_OR_EVENT_ID
            )
            args, kwargs = mock_get.call_args
            self.assertEqual(
                args,
                (
                    (
                        f"url/{ROOT}/{ASSETS_SUBPATH}/{ATTACHMENTS_ASSETS_EVENTS_LABEL}"
                        f"/{ASSET_OR_EVENT_ID}/{UUID}/info"
                    ),
                ),
                msg="INFO method called incorrectly",
            )
            self.assertEqual(
                kwargs,
                {
                    "headers": {
                        "authorization": "Bearer authauthauth",
                    },
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
