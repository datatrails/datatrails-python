"""
Test archivist
"""

from os import environ
from unittest import mock

from archivist.constants import ROOT, HEADERS_TOTAL_COUNT, HEADERS_RETRY_AFTER
from archivist.errors import (
    ArchivistBadFieldError,
    ArchivistBadRequestError,
    ArchivistTooManyRequestsError,
)
from archivist.logger import set_logger

from .mock_response import MockResponse
from .testarchivist import TestArchivistMethods


# pylint: disable=unused-variable
# pylint: disable=missing-docstring
# pylint: disable=protected-access

if "TEST_DEBUG" in environ and environ["TEST_DEBUG"]:
    set_logger(environ["TEST_DEBUG"])


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
                                "authorization": "Bearer authauthauth",
                            },
                            "params": None,
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
                                "authorization": "Bearer authauthauth",
                                "headerfield1": "headervalue1",
                            },
                            "params": None,
                            "verify": True,
                        },
                    ),
                    msg="GET method called incorrectly",
                )

    def test_list_with_params(self):
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
                    params={"paramsfield1": "paramsvalue1"},
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
                                "authorization": "Bearer authauthauth",
                            },
                            "verify": True,
                            "params": {"paramsfield1": "paramsvalue1"},
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
                        (f"url/{ROOT}/path/path",),
                        {
                            "headers": {
                                "authorization": "Bearer authauthauth",
                            },
                            "params": {"page_size": 2},
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
        paging = ({"page_size": 2}, {"page_size": 2, "page_token": "token"})
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
                        (f"url/{ROOT}/path/path",),
                        {
                            "headers": {
                                "authorization": "Bearer authauthauth",
                            },
                            "params": paging[i],
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

    def test_list_with_multiple_pages_and_params(self):
        """
        Test default list method
        """
        params = {"field2": "value2"}
        values = ("value10", "value11", "value12", "value13")
        paging = (
            {**params, "page_size": 2},
            {"page_size": 2, "page_token": "token"},
        )
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
                    params=params,
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
                        (f"url/{ROOT}/path/path",),
                        {
                            "headers": {
                                "authorization": "Bearer authauthauth",
                            },
                            "params": paging[i],
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
                                "authorization": "Bearer authauthauth",
                            },
                            "params": None,
                            "verify": True,
                        },
                    ),
                    msg="GET method called incorrectly",
                )
