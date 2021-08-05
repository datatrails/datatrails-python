"""
Test archivist
"""

from io import BytesIO
from unittest import TestCase, mock

from archivist.archivist import Archivist
from archivist.constants import ROOT, HEADERS_TOTAL_COUNT
from archivist.errors import (
    ArchivistBadFieldError,
    ArchivistBadRequestError,
    ArchivistDuplicateError,
    ArchivistIllegalArgumentError,
    ArchivistNotFoundError,
)

from .mock_response import MockResponse


# pylint: disable=unused-variable
# pylint: disable=missing-docstring
# pylint: disable=protected-access


class TestArchivist(TestCase):
    """
    Test Archivist class
    """

    def test_archivist(self):
        """
        Test default archivist creation
        """
        arch = Archivist("url", auth="authauthauth")
        self.assertIsNotNone(
            arch.assets,
            msg="Incorrect assets",
        )
        self.assertIsNotNone(
            arch.events,
            msg="Incorrect events",
        )
        self.assertIsNotNone(
            arch.locations,
            msg="Incorrect locations",
        )
        self.assertIsNotNone(
            arch.locations,
            msg="Incorrect locations",
        )
        self.assertIsNotNone(
            arch.attachments,
            msg="Incorrect attachments",
        )
        self.assertIsNotNone(
            arch.attachments,
            msg="Incorrect attachments",
        )
        self.assertEqual(
            arch.url,
            "url",
            msg="Incorrect url",
        )
        self.assertEqual(
            arch.headers,
            {
                "content-type": "application/json",
                "authorization": "Bearer authauthauth",
            },
            msg="Incorrect auth headers",
        )
        self.assertTrue(
            arch.verify,
            msg="verify must be True",
        )
        with self.assertRaises(AttributeError):
            e = arch.Illegal_endpoint

    def test_archivist_no_verify(self):
        """
        Test archivist creation with no verify
        """
        arch = Archivist("url", auth="authauthauth", verify=False)
        self.assertFalse(
            arch.verify,
            msg="verify must be False",
        )

    def test_archivist_with_neither_auth_and_cert(self):
        """
        Test archivist creation with both auth and cert
        """
        with self.assertRaises(ArchivistIllegalArgumentError):
            arch = Archivist("url")

    def test_archivist_with_both_auth_and_cert(self):
        """
        Test archivist creation with both auth and cert
        """
        with self.assertRaises(ArchivistIllegalArgumentError):
            arch = Archivist("url", auth="authauthauth", cert="/path/to/file")

    @mock.patch("archivist.archivist.os_path_isfile")
    def test_archivist_with_nonexistent_cert(self, mock_isfile):
        """
        Test archivist creation with nonexistent cert
        """
        mock_isfile.return_value = False
        with self.assertRaises(ArchivistNotFoundError):
            arch = Archivist("url", cert="/path/to/file")

    @mock.patch("archivist.archivist.os_path_isfile")
    def test_archivist_with_existent_cert(self, mock_isfile):
        """
        Test archivist creation with cert
        """
        mock_isfile.return_value = True
        arch = Archivist("url", cert="/path/to/file")
        self.assertEqual(
            arch.cert,
            "/path/to/file",
            msg="verify must be False",
        )


class TestArchivistMethods(TestCase):
    """
    Test Archivist base method class
    """

    def setUp(self):
        self.arch = Archivist("url", auth="authauthauth")


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
                        "cert": None,
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
                        "cert": None,
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
                4,
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


class TestArchivistGet(TestArchivistMethods):
    """
    Test Archivist Get method
    """

    def test_get(self):
        """
        Test default get method
        """
        with mock.patch.object(self.arch._session, "get") as mock_get:
            mock_get.return_value = MockResponse(200)
            resp = self.arch.get("path/path", "entity/xxxxxxxx")
            self.assertEqual(
                tuple(mock_get.call_args),
                (
                    (f"url/{ROOT}/path/path/entity/xxxxxxxx",),
                    {
                        "headers": {
                            "content-type": "application/json",
                            "authorization": "Bearer authauthauth",
                        },
                        "verify": True,
                        "cert": None,
                    },
                ),
                msg="GET method called incorrectly",
            )

    def test_ring_buffer(self):
        """
        Test That the ring buffer for response objects works as expected
        """
        with mock.patch.object(self.arch._session, "get") as mock_get:
            mock_get.return_value = MockResponse(200)
            resp = self.arch.get("path/path", "entity/xxxxxxxx")
            last_response = self.arch.last_response()
            self.assertEqual(last_response, [mock_get.return_value])

    def test_get_with_error(self):
        """
        Test get method with error
        """
        with mock.patch.object(self.arch._session, "get") as mock_get:
            mock_get.return_value = MockResponse(404, identity="entity/xxxxxxxx")
            with self.assertRaises(ArchivistNotFoundError):
                resp = self.arch.get("path/path", "entity/xxxxxxxx")

    def test_get_file(self):
        """
        Test default get method
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
                identity="entity/xxxxxxxx",
                iter_content=iter_content(),
            )
            with BytesIO() as fd:
                resp = self.arch.get_file("path/path", "entity/xxxxxxxx", fd)
                self.assertEqual(
                    tuple(mock_get.call_args),
                    (
                        (f"url/{ROOT}/path/path/entity/xxxxxxxx",),
                        {
                            "headers": {
                                "content-type": "application/json",
                                "authorization": "Bearer authauthauth",
                            },
                            "verify": True,
                            "cert": None,
                            "stream": True,
                        },
                    ),
                    msg="GET method called incorrectly",
                )

    def test_get_file_with_error(self):
        """
        Test get method with error
        """
        with mock.patch.object(self.arch._session, "get") as mock_get:
            mock_get.return_value = MockResponse(404, identity="entity/xxxxxxxx")
            with self.assertRaises(ArchivistNotFoundError):
                with BytesIO() as fd:
                    resp = self.arch.get_file("path/path", "entity/xxxxxxxx", fd)

    def test_get_with_headers(self):
        """
        Test default get method
        """
        with mock.patch.object(self.arch._session, "get") as mock_get:
            mock_get.return_value = MockResponse(200)
            resp = self.arch.get(
                "path/path",
                "id/xxxxxxxx",
                headers={"headerfield1": "headervalue1"},
            )
            self.assertEqual(
                tuple(mock_get.call_args),
                (
                    (f"url/{ROOT}/path/path/id/xxxxxxxx",),
                    {
                        "headers": {
                            "content-type": "application/json",
                            "authorization": "Bearer authauthauth",
                            "headerfield1": "headervalue1",
                        },
                        "verify": True,
                        "cert": None,
                    },
                ),
                msg="GET method called incorrectly",
            )


class TestArchivistDelete(TestArchivistMethods):
    """
    Test Archivist Delete method
    """

    def test_delete(self):
        """
        Test default delete method
        """
        with mock.patch.object(self.arch._session, "delete") as mock_delete:
            mock_delete.return_value = MockResponse(200)
            resp = self.arch.delete("path/path", "entity/xxxxxxxx")
            self.assertEqual(
                tuple(mock_delete.call_args),
                (
                    (f"url/{ROOT}/path/path/entity/xxxxxxxx",),
                    {
                        "headers": {
                            "content-type": "application/json",
                            "authorization": "Bearer authauthauth",
                        },
                        "verify": True,
                        "cert": None,
                    },
                ),
                msg="DELETE method called incorrectly",
            )

    def test_delete_with_error(self):
        """
        Test delete method with error
        """
        with mock.patch.object(self.arch._session, "delete") as mock_delete:
            mock_delete.return_value = MockResponse(404, identity="entity/xxxxxxxx")
            with self.assertRaises(ArchivistNotFoundError):
                resp = self.arch.delete("path/path", "entity/xxxxxxxx")

    def test_delete_with_headers(self):
        """
        Test default delete method
        """
        with mock.patch.object(self.arch._session, "delete") as mock_delete:
            mock_delete.return_value = MockResponse(200)
            resp = self.arch.delete(
                "path/path",
                "id/xxxxxxxx",
                headers={"headerfield1": "headervalue1"},
            )
            self.assertEqual(
                tuple(mock_delete.call_args),
                (
                    (f"url/{ROOT}/path/path/id/xxxxxxxx",),
                    {
                        "headers": {
                            "content-type": "application/json",
                            "authorization": "Bearer authauthauth",
                            "headerfield1": "headervalue1",
                        },
                        "verify": True,
                        "cert": None,
                    },
                ),
                msg="DELETE method called incorrectly",
            )


class TestArchivistPatch(TestArchivistMethods):
    """
    Test Archivist PATCH method
    """

    def test_patch(self):
        """
        Test default patch method
        """
        request = {"field1": "value1"}
        with mock.patch.object(self.arch._session, "patch") as mock_patch:
            mock_patch.return_value = MockResponse(200, request=request)
            resp = self.arch.patch("path/path", "entity/xxxx", request)
            self.assertEqual(
                tuple(mock_patch.call_args),
                (
                    (f"url/{ROOT}/path/path/entity/xxxx",),
                    {
                        "data": '{"field1": "value1"}',
                        "headers": {
                            "content-type": "application/json",
                            "authorization": "Bearer authauthauth",
                        },
                        "verify": True,
                        "cert": None,
                    },
                ),
                msg="POST method called incorrectly",
            )

    def test_patch_with_error(self):
        """
        Test post method with error
        """
        request = {"field1": "value1"}
        with mock.patch.object(self.arch._session, "patch") as mock_patch:
            mock_patch.return_value = MockResponse(
                400, request=request, field1="value1"
            )
            with self.assertRaises(ArchivistBadRequestError):
                resp = self.arch.patch("path/path", "entity/xxxx", request)

    def test_patch_with_headers(self):
        """
        Test default patch method
        """
        request = {"field1": "value1"}
        with mock.patch.object(self.arch._session, "patch") as mock_patch:
            mock_patch.return_value = MockResponse(200, request=request)
            resp = self.arch.patch(
                "path/path",
                "entity/xxxx",
                request,
                headers={"headerfield1": "headervalue1"},
            )
            self.assertEqual(
                tuple(mock_patch.call_args),
                (
                    (f"url/{ROOT}/path/path/entity/xxxx",),
                    {
                        "data": '{"field1": "value1"}',
                        "headers": {
                            "content-type": "application/json",
                            "authorization": "Bearer authauthauth",
                            "headerfield1": "headervalue1",
                        },
                        "verify": True,
                        "cert": None,
                    },
                ),
                msg="PATCH method called incorrectly",
            )


class TestArchivistCount(TestArchivistMethods):
    """
    Test Archivist count method
    """

    def test_count(self):
        """
        Test default count method
        """
        with mock.patch.object(self.arch._session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                headers={HEADERS_TOTAL_COUNT: 1},
                things=[
                    {
                        "field1": "value1",
                    },
                ],
            )
            count = self.arch.count("path/path")
            self.assertEqual(
                count,
                1,
                msg="incorrect count",
            )

    def test_count_with_error(self):
        """
        Test default count method with error
        """
        with mock.patch.object(self.arch._session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                400,
                things=[
                    {
                        "field1": "value1",
                    },
                ],
            )
            with self.assertRaises(ArchivistBadRequestError):
                count = self.arch.count("path/path")


class TestArchivistList(TestArchivistMethods):
    """
    Test Archivist list method
    """

    def test_list(self):
        """
        Test default list method
        """
        with mock.patch.object(self.arch._session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                things=[
                    {
                        "field1": "value1",
                    },
                ],
            )
            responses = list(self.arch.list("path/path", "things"))
            self.assertEqual(
                len(responses),
                1,
                msg="incorrect number of responses",
            )
            for a in mock_get.call_args_list:
                self.assertEqual(
                    tuple(a),
                    (
                        (f"url/{ROOT}/path/path",),
                        {
                            "headers": {
                                "content-type": "application/json",
                                "authorization": "Bearer authauthauth",
                            },
                            "verify": True,
                            "cert": None,
                        },
                    ),
                    msg="GET method called incorrectly",
                )

    def test_list_with_error(self):
        """
        Test default list method with error
        """
        with mock.patch.object(self.arch._session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                400,
                things=[
                    {
                        "field1": "value1",
                    },
                ],
            )
            with self.assertRaises(ArchivistBadRequestError):
                responses = list(self.arch.list("path/path", "things"))

    def test_list_with_bad_field(self):
        """
        Test default list method with error
        """
        with mock.patch.object(self.arch._session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                things=[
                    {
                        "field1": "value1",
                    },
                ],
            )
            with self.assertRaises(ArchivistBadFieldError):
                responses = list(self.arch.list("path/path", "badthings"))

    def test_list_with_headers(self):
        """
        Test default list method
        """
        with mock.patch.object(self.arch._session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                things=[
                    {
                        "field1": "value1",
                    },
                ],
            )
            responses = list(
                self.arch.list(
                    "path/path",
                    "things",
                    headers={"headerfield1": "headervalue1"},
                )
            )
            self.assertEqual(
                len(responses),
                1,
                msg="incorrect number of responses",
            )
            for a in mock_get.call_args_list:
                self.assertEqual(
                    tuple(a),
                    (
                        (f"url/{ROOT}/path/path",),
                        {
                            "headers": {
                                "content-type": "application/json",
                                "authorization": "Bearer authauthauth",
                                "headerfield1": "headervalue1",
                            },
                            "verify": True,
                            "cert": None,
                        },
                    ),
                    msg="GET method called incorrectly",
                )

    def test_list_with_query(self):
        """
        Test default list method
        """
        with mock.patch.object(self.arch._session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                things=[
                    {
                        "field1": "value1",
                    },
                ],
            )
            responses = list(
                self.arch.list(
                    "path/path",
                    "things",
                    query={"queryfield1": "queryvalue1"},
                )
            )
            self.assertEqual(
                len(responses),
                1,
                msg="incorrect number of responses",
            )
            for a in mock_get.call_args_list:
                self.assertEqual(
                    tuple(a),
                    (
                        (f"url/{ROOT}/path/path?queryfield1=queryvalue1",),
                        {
                            "headers": {
                                "content-type": "application/json",
                                "authorization": "Bearer authauthauth",
                            },
                            "verify": True,
                            "cert": None,
                        },
                    ),
                    msg="GET method called incorrectly",
                )

    def test_list_with_page_size(self):
        """
        Test default list method
        """
        values = ("value10", "value11")
        with mock.patch.object(self.arch._session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                things=[
                    {
                        "field1": values[0],
                    },
                    {
                        "field1": values[1],
                    },
                ],
            )
            responses = list(
                self.arch.list(
                    "path/path",
                    "things",
                    page_size=2,
                )
            )
            self.assertEqual(
                len(responses),
                2,
                msg="incorrect number of responses",
            )
            for a in mock_get.call_args_list:
                self.assertEqual(
                    tuple(a),
                    (
                        (f"url/{ROOT}/path/path?page_size=2",),
                        {
                            "headers": {
                                "content-type": "application/json",
                                "authorization": "Bearer authauthauth",
                            },
                            "verify": True,
                            "cert": None,
                        },
                    ),
                    msg="GET method called incorrectly",
                )

            for i, r in enumerate(responses):
                self.assertEqual(
                    r["field1"],
                    values[i],
                    msg="Incorrect response body value",
                )

    def test_list_with_multiple_pages(self):
        """
        Test default list method
        """
        values = ("value10", "value11", "value12", "value13")
        paging = ("page_size=2", "page_token=token")
        with mock.patch.object(self.arch._session, "get") as mock_get:
            mock_get.side_effect = [
                MockResponse(
                    200,
                    things=[
                        {
                            "field1": values[0],
                        },
                        {
                            "field1": values[1],
                        },
                    ],
                    next_page_token="token",
                ),
                MockResponse(
                    200,
                    things=[
                        {
                            "field1": values[2],
                        },
                        {
                            "field1": values[3],
                        },
                    ],
                ),
            ]
            responses = list(
                self.arch.list(
                    "path/path",
                    "things",
                    page_size=2,
                )
            )
            self.assertEqual(
                len(responses),
                4,
                msg="incorrect number of responses",
            )
            for i, a in enumerate(mock_get.call_args_list):
                self.assertEqual(
                    tuple(a),
                    (
                        (f"url/{ROOT}/path/path?{paging[i]}",),
                        {
                            "headers": {
                                "content-type": "application/json",
                                "authorization": "Bearer authauthauth",
                            },
                            "verify": True,
                            "cert": None,
                        },
                    ),
                    msg="GET method called incorrectly",
                )

            for i, r in enumerate(responses):
                self.assertEqual(
                    r["field1"],
                    values[i],
                    msg="Incorrect response body value",
                )


class TestArchivistSignature(TestArchivistMethods):
    """
    Test Archivist get_by_signature method
    """

    def test_get_by_signature(self):
        """
        Test default get_by_signature method
        """
        with mock.patch.object(self.arch._session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                things=[
                    {
                        "field1": "value1",
                    },
                ],
            )
            entity = self.arch.get_by_signature(
                "path/path", "things", {"field1": "value1"}
            )
            for a in mock_get.call_args_list:
                self.assertEqual(
                    tuple(a),
                    (
                        (f"url/{ROOT}/path/path?page_size=2&field1=value1",),
                        {
                            "headers": {
                                "content-type": "application/json",
                                "authorization": "Bearer authauthauth",
                            },
                            "verify": True,
                            "cert": None,
                        },
                    ),
                    msg="GET method called incorrectly",
                )

    def test_get_by_signature_not_found(self):
        """
        Test default get_by_signature method
        """
        with mock.patch.object(self.arch._session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                things=[],
            )
            with self.assertRaises(ArchivistNotFoundError):
                entity = self.arch.get_by_signature(
                    "path/path", "things", {"field1": "value1"}
                )

    def test_get_by_signature_duplicate(self):
        """
        Test default get_by_signature method
        """
        with mock.patch.object(self.arch._session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                things=[
                    {
                        "field1": "value1",
                    },
                    {
                        "field1": "value1",
                    },
                ],
            )
            with self.assertRaises(ArchivistDuplicateError):
                entity = self.arch.get_by_signature(
                    "path/path", "things", {"field1": "value1"}
                )

    def test_get_by_signature_with_bad_field(self):
        """
        Test default list method with error
        """
        with mock.patch.object(self.arch._session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                things=[
                    {
                        "field1": "value1",
                    },
                ],
            )
            with self.assertRaises(ArchivistBadFieldError):
                entity = self.arch.get_by_signature(
                    "path/path", "badthings", {"field1": "value1"}
                )
