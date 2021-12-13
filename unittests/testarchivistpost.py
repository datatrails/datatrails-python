"""
Test archivist
"""

from io import BytesIO
from unittest import TestCase, mock

from archivist.archivist import Archivist
from archivist.constants import ROOT, HEADERS_RETRY_AFTER
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


class TestArchivistPost(TestArchivistMethods):
    """
    Test Archivist POST method
    """

    def test_post(self):
        """
        Test default post method
        """
        request = {"field1": "value1"}
        with mock.patch.object(self.arch._session, "post") as mock_post:
            mock_post.return_value = MockResponse(200, request=request)
            resp = self.arch.post("path/path", request)
            self.assertEqual(
                tuple(mock_post.call_args),
                (
                    (f"url/{ROOT}/path/path",),
                    {
                        "data": '{"field1": "value1"}',
                        "headers": {
                            "content-type": "application/json",
                            "authorization": "Bearer authauthauth",
                        },
                        "verify": True,
                    },
                ),
                msg="POST method called incorrectly",
            )

    def test_post_with_error(self):
        """
        Test post method with error
        """
        request = {"field1": "value1"}
        with mock.patch.object(self.arch._session, "post") as mock_post:
            mock_post.return_value = MockResponse(400, request=request, field1="value1")
            with self.assertRaises(ArchivistBadRequestError):
                resp = self.arch.post("path/path", request)

    def test_post_with_429(self):
        """
        Test post method with 429
        """
        request = {"field1": "value1"}
        with mock.patch.object(self.arch._session, "post") as mock_post:
            mock_post.return_value = MockResponse(429, request=request, field1="value1")
            with self.assertRaises(ArchivistTooManyRequestsError):
                resp = self.arch.post("path/path", request)

    def test_post_with_429_retry_and_fail(self):
        """
        Test post method with 429 retry and fail
        """
        request = {"field1": "value1"}
        with mock.patch.object(self.arch._session, "post") as mock_post:
            mock_post.side_effect = (
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(429),
            )
            with self.assertRaises(ArchivistTooManyRequestsError):
                resp = self.arch.post("path/path", request)

    def test_post_with_429_retry_and_retries_fail(self):
        """
        Test post method with 429 retry and retries_fail
        """
        request = {"field1": "value1"}
        with mock.patch.object(self.arch._session, "post") as mock_post:
            mock_post.side_effect = (
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
            )
            with self.assertRaises(ArchivistTooManyRequestsError):
                resp = self.arch.post("path/path", request)

    def test_post_with_429_retry_and_success(self):
        """
        Test post method with 429 retry and success
        """
        request = {"field1": "value1"}
        with mock.patch.object(self.arch._session, "post") as mock_post:
            mock_post.side_effect = (
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(200),
            )
            resp = self.arch.post("path/path", request)
            self.assertEqual(
                tuple(mock_post.call_args),
                (
                    (f"url/{ROOT}/path/path",),
                    {
                        "data": '{"field1": "value1"}',
                        "headers": {
                            "content-type": "application/json",
                            "authorization": "Bearer authauthauth",
                        },
                        "verify": True,
                    },
                ),
                msg="POST method called incorrectly",
            )

    def test_post_with_headers(self):
        """
        Test default post method
        """
        request = {"field1": "value1"}
        with mock.patch.object(self.arch._session, "post") as mock_post:
            mock_post.return_value = MockResponse(200, request=request)
            resp = self.arch.post(
                "path/path",
                request,
                headers={"headerfield1": "headervalue1"},
            )
            self.assertEqual(
                tuple(mock_post.call_args),
                (
                    (f"url/{ROOT}/path/path",),
                    {
                        "data": '{"field1": "value1"}',
                        "headers": {
                            "content-type": "application/json",
                            "authorization": "Bearer authauthauth",
                            "headerfield1": "headervalue1",
                        },
                        "verify": True,
                    },
                ),
                msg="POST method called incorrectly",
            )

    def test_post_file(self):
        """
        Test default post_file method
        """
        with mock.patch.object(self.arch._session, "post") as mock_post:
            mock_post.return_value = MockResponse(200)
            resp = self.arch.post_file(
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
                f"url/{ROOT}/path/path",
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
            self.assertTrue(
                headers["content-type"].startswith("multipart/form-data"),
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
        with mock.patch.object(self.arch._session, "post") as mock_post:
            mock_post.return_value = MockResponse(200)
            resp = self.arch.post_file(
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
                f"url/{ROOT}/path/path?field1=value1&field2=value2",
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
            self.assertTrue(
                headers["content-type"].startswith("multipart/form-data"),
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
        with mock.patch.object(self.arch._session, "post") as mock_post:
            mock_post.return_value = MockResponse(400)
            with self.assertRaises(ArchivistBadRequestError):
                resp = self.arch.post_file(
                    "path/path",
                    BytesIO(b"lotsofbytes"),
                    "image/jpg",
                )

    def test_post_file_with_429(self):
        """
        Test post method with error
        """
        with mock.patch.object(self.arch._session, "post") as mock_post:
            mock_post.return_value = MockResponse(429)
            with self.assertRaises(ArchivistTooManyRequestsError):
                resp = self.arch.post_file(
                    "path/path",
                    BytesIO(b"lotsofbytes"),
                    "image/jpg",
                )

    def test_post_file_with_429_retry_and_fail(self):
        """
        Test post method with 429 retry and fail
        """
        with mock.patch.object(self.arch._session, "post") as mock_post:
            mock_post.side_effect = (
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(429),
            )
            with self.assertRaises(ArchivistTooManyRequestsError):
                resp = self.arch.post_file(
                    "path/path",
                    BytesIO(b"lotsofbytes"),
                    "image/jpg",
                )

    def test_post_file_with_429_retry_and_retries_fail(self):
        """
        Test post method with 429 retry and retries_fail
        """
        with mock.patch.object(self.arch._session, "post") as mock_post:
            mock_post.side_effect = (
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
            )
            with self.assertRaises(ArchivistTooManyRequestsError):
                resp = self.arch.post_file(
                    "path/path",
                    BytesIO(b"lotsofbytes"),
                    "image/jpg",
                )

    def test_post_file_with_429_retry_and_success(self):
        """
        Test post method with 429 retry and success
        """
        with mock.patch.object(self.arch._session, "post") as mock_post:
            mock_post.side_effect = (
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(200),
            )
            resp = self.arch.post_file(
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
                f"url/{ROOT}/path/path",
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
            self.assertTrue(
                headers["content-type"].startswith("multipart/form-data"),
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
        with mock.patch.object(self.arch._session, "post") as mock_post:
            mock_post.return_value = MockResponse(200, request=request)
            resp = self.arch.post("path/path", request)
            self.assertEqual(
                tuple(mock_post.call_args),
                (
                    (f"url/{ROOT}/path/path",),
                    {
                        "data": '{"field1": "value1"}',
                        "headers": {
                            "content-type": "application/json",
                        },
                        "verify": True,
                    },
                ),
                msg="POST method called incorrectly",
            )
