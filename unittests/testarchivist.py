"""
Test archivist
"""

from copy import copy
from json import loads as json_loads
from os import environ
from unittest import TestCase, mock

from archivist.archivist import Archivist
from archivist.constants import ROOT, HEADERS_TOTAL_COUNT, HEADERS_RETRY_AFTER
from archivist.errors import (
    ArchivistBadFieldError,
    ArchivistBadRequestError,
    ArchivistDuplicateError,
    ArchivistHeaderError,
    ArchivistNotFoundError,
    ArchivistTooManyRequestsError,
)
from archivist.logger import set_logger

from .mock_response import MockResponse


# pylint: disable=unused-variable
# pylint: disable=missing-docstring
# pylint: disable=protected-access

if "TEST_DEBUG" in environ and environ["TEST_DEBUG"]:
    set_logger(environ["TEST_DEBUG"])


CLIENT_ID = "client_id-2f78-4fa0-9425-d59314845bc5"
CLIENT_SECRET = "client_secret-388f5187e32d930d83"
ACCESS_TOKEN = "access_token-xbXATAWrEpepR7TklOxRB-yud92AsD6DGGasiEGN7MZKT0AIQ4Rw9s"
REQUEST = {
    "grant_type": "client_credentials",
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
}

RESPONSE = {
    "access_token": ACCESS_TOKEN,
    "expires_in": 660,
    "token_type": "Bearer",
}


class TestArchivist(TestCase):
    """
    Test Archivist class
    """

    def test_archivist(self):
        """
        Test default archivist creation
        """
        arch = Archivist("url", "authauthauth")
        self.assertEqual(
            str(arch),
            "Archivist(url)",
            msg="Incorrect str",
        )
        self.assertEqual(
            str(arch.access_policies),
            "AccessPoliciesClient(url)",
            msg="Incorrect access_policies",
        )
        self.assertEqual(
            str(arch.appidp),
            "AppIDPClient(url)",
            msg="Incorrect appidp",
        )
        self.assertEqual(
            str(arch.applications),
            "ApplicationsClient(url)",
            msg="Incorrect applications",
        )
        self.assertEqual(
            str(arch.assets),
            "AssetsClient(url)",
            msg="Incorrect assets",
        )
        self.assertEqual(
            str(arch.attachments),
            "AttachmentsClient(url)",
            msg="Incorrect attachments",
        )
        self.assertEqual(
            str(arch.compliance),
            "ComplianceClient(url)",
            msg="Incorrect compliance",
        )
        self.assertEqual(
            str(arch.compliance_policies),
            "CompliancePoliciesClient(url)",
            msg="Incorrect compliance_policies",
        )
        self.assertEqual(
            str(arch.events),
            "EventsClient(url)",
            msg="Incorrect events",
        )
        self.assertEqual(
            str(arch.locations),
            "LocationsClient(url)",
            msg="Incorrect locations",
        )
        self.assertEqual(
            str(arch.runner),
            "Runner(url)",
            msg="Incorrect runner",
        )
        self.assertEqual(
            str(arch.sboms),
            "SBOMSClient(url)",
            msg="Incorrect sboms",
        )
        self.assertEqual(
            str(arch.subjects),
            "SubjectsClient(url)",
            msg="Incorrect subjects",
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
            },
            msg="Incorrect headers",
        )
        self.assertEqual(
            arch.auth,
            "authauthauth",
            msg="Incorrect auth",
        )
        self.assertTrue(
            arch.verify,
            msg="verify must be True",
        )
        with self.assertRaises(AttributeError):
            e = arch.Illegal_endpoint

    def test_archivist_token(self):
        """
        Test archivist creation with app registration
        """
        arch = Archivist("url", (CLIENT_ID, CLIENT_SECRET))
        with mock.patch.object(arch.appidp, "token") as mock_token:
            mock_token.return_value = RESPONSE
            self.assertEqual(
                arch.auth,
                ACCESS_TOKEN,
                msg="Incorrect auth",
            )

    def test_archivist_copy(self):
        """
        Test archivist copy
        """
        arch = Archivist("url", "authauthauth", verify=False)
        arch1 = copy(arch)
        self.assertEqual(
            arch.url,
            arch1.url,
            msg="Incorrect url",
        )
        self.assertEqual(
            arch.headers,
            arch1.headers,
            msg="Incorrect auth headers",
        )
        self.assertEqual(
            arch.verify,
            arch1.verify,
            msg="Incorrect verify",
        )
        self.assertEqual(
            arch.fixtures,
            arch1.fixtures,
            msg="Incorrect fixtures",
        )

    def test_archivist_no_verify(self):
        """
        Test archivist creation with no verify
        """
        arch = Archivist("url", "authauthauth", verify=False)
        self.assertFalse(
            arch.verify,
            msg="verify must be False",
        )


class TestArchivistMethods(TestCase):
    """
    Test Archivist base method class
    """

    def setUp(self):
        self.arch = Archivist("url", "authauthauth")


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
            args, kwargs = mock_patch.call_args
            self.assertEqual(
                args,
                (f"url/{ROOT}/path/path/entity/xxxx",),
                msg="POST method args called incorrectly",
            )
            kwargs["data"] = json_loads(kwargs["data"])
            self.assertEqual(
                kwargs,
                {
                    "data": request,
                    "headers": {
                        "content-type": "application/json",
                        "authorization": "Bearer authauthauth",
                    },
                    "verify": True,
                },
                msg="POST method kwargs called incorrectly",
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
            args, kwargs = mock_patch.call_args
            self.assertEqual(
                args,
                (f"url/{ROOT}/path/path/entity/xxxx",),
                msg="PATCH method args called incorrectly",
            )
            kwargs["data"] = json_loads(kwargs["data"])
            self.assertEqual(
                kwargs,
                {
                    "data": request,
                    "headers": {
                        "content-type": "application/json",
                        "authorization": "Bearer authauthauth",
                        "headerfield1": "headervalue1",
                    },
                    "verify": True,
                },
                msg="PATCH method kwargs called incorrectly",
            )

    def test_patch_with_429(self):
        """
        Test patch method with error
        """
        request = {"field1": "value1"}
        with mock.patch.object(self.arch._session, "patch") as mock_patch:
            mock_patch.return_value = MockResponse(429, request=request)
            with self.assertRaises(ArchivistTooManyRequestsError):
                resp = self.arch.patch(
                    "path/path",
                    "id/xxxxxxxx",
                    request,
                )

    def test_patch_with_429_retry_and_fail(self):
        """
        Test patch method with 429 retry and fail
        """
        request = {"field1": "value1"}
        with mock.patch.object(self.arch._session, "patch") as mock_patch:
            mock_patch.side_effect = (
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}, request=request),
                MockResponse(429, request=request),
            )
            with self.assertRaises(ArchivistTooManyRequestsError):
                resp = self.arch.patch(
                    "path/path",
                    "id/xxxxxxxx",
                    request,
                )

    def test_patch_with_429_retry_and_retries_fail(self):
        """
        Test patch method with 429 retry and retries_fail
        """
        request = {"field1": "value1"}
        with mock.patch.object(self.arch._session, "patch") as mock_patch:
            mock_patch.side_effect = (
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}, request=request),
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}, request=request),
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}, request=request),
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}, request=request),
            )
            with self.assertRaises(ArchivistTooManyRequestsError):
                resp = self.arch.patch(
                    "path/path",
                    "id/xxxxxxxx",
                    request,
                )

    def test_patch_with_429_retry_and_success(self):
        """
        Test patch method with 429 retry and success
        """
        request = {"field1": "value1"}
        with mock.patch.object(self.arch._session, "patch") as mock_patch:
            mock_patch.side_effect = (
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}, request=request),
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}, request=request),
                MockResponse(200, request=request),
            )
            resp = self.arch.patch("path/path", "entity/xxxxxxxx", request)
            args, kwargs = mock_patch.call_args
            self.assertEqual(
                args,
                (f"url/{ROOT}/path/path/entity/xxxxxxxx",),
                msg="PATCH method args called incorrectly",
            )
            self.assertEqual(
                kwargs,
                {
                    "data": '{"field1": "value1"}',
                    "headers": {
                        "content-type": "application/json",
                        "authorization": "Bearer authauthauth",
                    },
                    "verify": True,
                },
                msg="PATCH method kwargs called incorrectly",
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
                headers={HEADERS_TOTAL_COUNT.lower(): 1},
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

    def test_count_with_missing_count_error(self):
        """
        Tests the default count method raises a ArchivistHeaderError when the
        expected count header field is missing
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
            with self.assertRaises(ArchivistHeaderError):
                count = self.arch.count("path/path")

    def test_count_with_429(self):
        """
        Test count method with error
        """
        with mock.patch.object(self.arch._session, "get") as mock_get:
            mock_get.return_value = MockResponse(429)
            with self.assertRaises(ArchivistTooManyRequestsError):
                count = self.arch.count("path/path")

    def test_count_with_429_retry_and_fail(self):
        """
        Test count method with 429 retry and fail
        """
        with mock.patch.object(self.arch._session, "get") as mock_get:
            mock_get.side_effect = (
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(429),
            )
            with self.assertRaises(ArchivistTooManyRequestsError):
                count = self.arch.count("path/path")

    def test_count_with_429_retry_and_retries_fail(self):
        """
        Test count method with 429 retry and retries_fail
        """
        with mock.patch.object(self.arch._session, "get") as mock_get:
            mock_get.side_effect = (
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
            )
            with self.assertRaises(ArchivistTooManyRequestsError):
                count = self.arch.count("path/path")

    def test_count_with_429_retry_and_success(self):
        """
        Test count method with 429 retry and success
        """
        with mock.patch.object(self.arch._session, "get") as mock_get:
            mock_get.side_effect = (
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(
                    200,
                    headers={HEADERS_TOTAL_COUNT: 1},
                    things=[
                        {
                            "field1": "value1",
                        },
                    ],
                ),
            )
            count = self.arch.count("path/path")
            self.assertEqual(
                count,
                1,
                msg="incorrect count",
            )


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

    def test_list_with_429(self):
        """
        Test list method with error
        """
        with mock.patch.object(self.arch._session, "get") as mock_get:
            mock_get.return_value = MockResponse(429)
            with self.assertRaises(ArchivistTooManyRequestsError):
                things = list(self.arch.list("path/path", "things"))

    def test_list_with_429_retry_and_fail(self):
        """
        Test list method with 429 retry and fail
        """
        with mock.patch.object(self.arch._session, "get") as mock_get:
            mock_get.side_effect = (
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(429),
            )
            with self.assertRaises(ArchivistTooManyRequestsError):
                things = list(self.arch.list("path/path", "things"))

    def test_list_with_429_retry_and_retries_fail(self):
        """
        Test list method with 429 retry and retries_fail
        """
        with mock.patch.object(self.arch._session, "get") as mock_get:
            mock_get.side_effect = (
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
            )
            with self.assertRaises(ArchivistTooManyRequestsError):
                things = list(self.arch.list("path/path", "things"))

    def test_list_with_429_retry_and_success(self):
        """
        Test list method with 429 retry and success
        """
        with mock.patch.object(self.arch._session, "get") as mock_get:
            mock_get.side_effect = (
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(
                    200,
                    headers={HEADERS_TOTAL_COUNT: 1},
                    things=[
                        {
                            "field1": "value1",
                        },
                    ],
                ),
            )
            things = list(self.arch.list("path/path", "things"))
            self.assertEqual(
                len(things),
                1,
                msg="incorrect number of things",
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
                        },
                    ),
                    msg="GET method called incorrectly",
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
