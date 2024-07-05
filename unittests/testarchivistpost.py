"""
Test archivist post
"""

from io import BytesIO
from unittest import TestCase, mock

from archivist.about import __version__ as VERSION
from archivist.archivist import Archivist
from archivist.constants import (
    HEADERS_RETRY_AFTER,
    USER_AGENT,
    USER_AGENT_PREFIX,
)
from archivist.errors import (
    ArchivistBadRequestError,
    ArchivistTooManyRequestsError,
)

from .mock_response import MockResponse

# pylint: disable=unused-variable
# pylint: disable=missing-docstring
# pylint: disable=protected-access


class TestArchivistMethods(TestCase):
    """
    Test Archivist base method class
    """

    def setUp(self):
        self.arch = Archivist("url", "authauthauth")

    def tearDown(self):
        self.arch.close()


class TestArchivistPost(TestArchivistMethods):
    """
    Test Archivist POST method
    """

    def test_post(self):
        """
        Test default post method
        """
        request = {"field1": "value1"}
        with mock.patch.object(self.arch.session, "post") as mock_post:
            mock_post.return_value = MockResponse(200, request=request)
            self.arch.post("path/path", request)
            args, kwargs = mock_post.call_args
            self.assertEqual(
                args,
                ("path/path",),
                msg="POST method args called incorrectly",
            )
            self.assertEqual(
                kwargs,
                {
                    "json": request,
                    "headers": {
                        "authorization": "Bearer authauthauth",
                        USER_AGENT: f"{USER_AGENT_PREFIX}{VERSION}",
                    },
                },
                msg="POST method kwargs called incorrectly",
            )

    def test_post_with_error(self):
        """
        Test post method with error
        """
        request = {"field1": "value1"}
        with mock.patch.object(self.arch.session, "post") as mock_post:
            mock_post.return_value = MockResponse(400, request=request, field1="value1")
            with self.assertRaises(ArchivistBadRequestError):
                self.arch.post("path/path", request)

    def test_post_with_429(self):
        """
        Test post method with 429
        """
        request = {"field1": "value1"}
        with mock.patch.object(self.arch.session, "post") as mock_post:
            mock_post.return_value = MockResponse(429, request=request, field1="value1")
            with self.assertRaises(ArchivistTooManyRequestsError):
                self.arch.post("path/path", request)

    def test_post_with_429_retry_and_fail(self):
        """
        Test post method with 429 retry and fail
        """
        request = {"field1": "value1"}
        with mock.patch.object(self.arch.session, "post") as mock_post:
            mock_post.side_effect = (
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(429),
            )
            with self.assertRaises(ArchivistTooManyRequestsError):
                self.arch.post("path/path", request)

    def test_post_with_429_retry_and_retries_fail(self):
        """
        Test post method with 429 retry and retries_fail
        """
        request = {"field1": "value1"}
        with mock.patch.object(self.arch.session, "post") as mock_post:
            mock_post.side_effect = (
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
            )
            with self.assertRaises(ArchivistTooManyRequestsError):
                self.arch.post("path/path", request)

    def test_post_with_429_retry_and_success(self):
        """
        Test post method with 429 retry and success
        """
        request = {"field1": "value1"}
        with mock.patch.object(self.arch.session, "post") as mock_post:
            mock_post.side_effect = (
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(200),
            )
            self.arch.post("path/path", request)
            args, kwargs = mock_post.call_args
            self.assertEqual(
                args,
                ("path/path",),
                msg="POST method args called incorrectly",
            )
            self.assertEqual(
                kwargs,
                {
                    "json": request,
                    "headers": {
                        "authorization": "Bearer authauthauth",
                        USER_AGENT: f"{USER_AGENT_PREFIX}{VERSION}",
                    },
                },
                msg="POST method kwargs called incorrectly",
            )

    def test_post_with_headers(self):
        """
        Test default post method
        """
        request = {"field1": "value1"}
        with mock.patch.object(self.arch.session, "post") as mock_post:
            mock_post.return_value = MockResponse(200, request=request)
            self.arch.post(
                "path/path",
                request,
                headers={
                    "headerfield1": "headervalue1",
                    USER_AGENT: f"{USER_AGENT_PREFIX}{VERSION}",
                },
            )
            args, kwargs = mock_post.call_args
            self.assertEqual(
                args,
                ("path/path",),
                msg="POST method args called incorrectly",
            )
            self.assertEqual(
                kwargs,
                {
                    "json": request,
                    "headers": {
                        "authorization": "Bearer authauthauth",
                        "headerfield1": "headervalue1",
                        USER_AGENT: f"{USER_AGENT_PREFIX}{VERSION}",
                    },
                },
                msg="POST method kwargs called incorrectly",
            )

    def test_post_file(self):
        """
        Test default post_file method
        """
        with mock.patch.object(self.arch.session, "post") as mock_post:
            mock_post.return_value = MockResponse(200)
            self.arch.post_file(
                "path/path",
                BytesIO(b"lotsofbytes"),
                "image/jpg",
            )
            args, kwargs = mock_post.call_args
            self.assertEqual(
                len(args),
                1,
                msg="Incorrect number of arguments",
            )
            self.assertEqual(
                args[0],
                "path/path",
                msg="Incorrect first argument",
            )
            self.assertEqual(
                len(kwargs),
                3,
                msg="Incorrect number of keyword arguments",
            )
            headers = kwargs.get("headers")
            self.assertNotEqual(
                headers,
                None,
                msg="Header does not exist",
            )
            self.assertEqual(
                headers["content-type"].startswith("multipart/form-data"),
                True,
                msg="Incorrect content-type",
            )
            data = kwargs.get("data")
            self.assertIsNotNone(
                data,
                msg="Incorrect data",
            )
            fields = data.fields
            self.assertIsNotNone(
                fields,
                msg="Incorrect fields",
            )
            myfile = fields.get("file")
            self.assertIsNotNone(
                myfile,
                msg="Incorrect file key",
            )
            self.assertEqual(
                myfile[0],
                "filename",
                msg="Incorrect filename",
            )
            self.assertEqual(
                myfile[2],
                "image/jpg",
                msg="Incorrect mimetype",
            )

    def test_post_file_with_params(self):
        """
        Test default post_file method
        """
        with mock.patch.object(self.arch.session, "post") as mock_post:
            mock_post.return_value = MockResponse(200)
            self.arch.post_file(
                "path/path",
                BytesIO(b"lotsofbytes"),
                "image/jpg",
                params={"field1": "value1", "field2": "value2"},
            )
            args, kwargs = mock_post.call_args
            self.assertEqual(
                len(args),
                1,
                msg="Incorrect number of arguments",
            )
            self.assertEqual(
                args[0],
                "path/path",
                msg="Incorrect first argument",
            )
            self.assertEqual(
                len(kwargs),
                3,
                msg="Incorrect number of keyword arguments",
            )
            headers = kwargs.get("headers")
            self.assertNotEqual(
                headers,
                None,
                msg="Header does not exist",
            )
            self.assertEqual(
                headers["content-type"].startswith("multipart/form-data"),
                True,
                msg="Incorrect content-type",
            )
            data = kwargs.get("data")
            self.assertIsNotNone(
                data,
                msg="Incorrect data",
            )
            fields = data.fields
            self.assertIsNotNone(
                fields,
                msg="Incorrect fields",
            )
            myfile = fields.get("file")
            self.assertIsNotNone(
                myfile,
                msg="Incorrect file key",
            )
            self.assertEqual(
                myfile[0],
                "filename",
                msg="Incorrect filename",
            )
            self.assertEqual(
                myfile[2],
                "image/jpg",
                msg="Incorrect mimetype",
            )

    def test_post_file_with_error(self):
        """
        Test post method with error
        """
        with mock.patch.object(self.arch.session, "post") as mock_post:
            mock_post.return_value = MockResponse(400)
            with self.assertRaises(ArchivistBadRequestError):
                self.arch.post_file(
                    "path/path",
                    BytesIO(b"lotsofbytes"),
                    "image/jpg",
                )

    def test_post_file_with_429(self):
        """
        Test post method with error
        """
        with mock.patch.object(self.arch.session, "post") as mock_post:
            mock_post.return_value = MockResponse(429)
            with self.assertRaises(ArchivistTooManyRequestsError):
                self.arch.post_file(
                    "path/path",
                    BytesIO(b"lotsofbytes"),
                    "image/jpg",
                )

    def test_post_file_with_429_retry_and_fail(self):
        """
        Test post method with 429 retry and fail
        """
        with mock.patch.object(self.arch.session, "post") as mock_post:
            mock_post.side_effect = (
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(429),
            )
            with self.assertRaises(ArchivistTooManyRequestsError):
                self.arch.post_file(
                    "path/path",
                    BytesIO(b"lotsofbytes"),
                    "image/jpg",
                )

    def test_post_file_with_429_retry_and_retries_fail(self):
        """
        Test post method with 429 retry and retries_fail
        """
        with mock.patch.object(self.arch.session, "post") as mock_post:
            mock_post.side_effect = (
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
            )
            with self.assertRaises(ArchivistTooManyRequestsError):
                self.arch.post_file(
                    "path/path",
                    BytesIO(b"lotsofbytes"),
                    "image/jpg",
                )

    def test_post_file_with_429_retry_and_success(self):
        """
        Test post method with 429 retry and success
        """
        with mock.patch.object(self.arch.session, "post") as mock_post:
            mock_post.side_effect = (
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(200),
            )
            self.arch.post_file(
                "path/path",
                BytesIO(b"lotsofbytes"),
                "image/jpg",
            )
            args, kwargs = mock_post.call_args
            self.assertEqual(
                len(args),
                1,
                msg="Incorrect number of arguments",
            )
            self.assertEqual(
                args[0],
                "path/path",
                msg="Incorrect first argument",
            )
            self.assertEqual(
                len(kwargs),
                3,
                msg="Incorrect number of keyword arguments",
            )
            headers = kwargs.get("headers")
            self.assertNotEqual(
                headers,
                None,
                msg="Header does not exist",
            )
            self.assertEqual(
                headers["content-type"].startswith("multipart/form-data"),
                True,
                msg="Incorrect content-type",
            )
            data = kwargs.get("data")
            self.assertIsNotNone(
                data,
                msg="Incorrect data",
            )
            fields = data.fields
            self.assertIsNotNone(
                fields,
                msg="Incorrect fields",
            )
            myfile = fields.get("file")
            self.assertIsNotNone(
                myfile,
                msg="Incorrect file key",
            )
            self.assertEqual(
                myfile[0],
                "filename",
                msg="Incorrect filename",
            )
            self.assertEqual(
                myfile[2],
                "image/jpg",
                msg="Incorrect mimetype",
            )


class TestArchivistPostWithoutAuth(TestCase):
    """
    Test Archivist base method class
    """

    def setUp(self):
        self.arch = Archivist("url", None)

    def test_post_without_auth(self):
        """
        Test default post method
        """
        request = {"field1": "value1"}
        with mock.patch.object(self.arch.session, "post") as mock_post:
            mock_post.return_value = MockResponse(200, request=request)
            self.arch.post("path/path", request)
            args, kwargs = mock_post.call_args
            self.assertEqual(
                args,
                ("path/path",),
                msg="POST method args called incorrectly",
            )
            self.assertEqual(
                kwargs,
                {
                    "json": request,
                    "headers": {
                        USER_AGENT: f"{USER_AGENT_PREFIX}{VERSION}",
                    },
                },
                msg="POST method kwargs called incorrectly",
            )
