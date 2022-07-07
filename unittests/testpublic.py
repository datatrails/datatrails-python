"""
Test public
"""

from copy import copy
from os import environ
from unittest import TestCase, mock

from archivist.constants import HEADERS_TOTAL_COUNT, HEADERS_RETRY_AFTER
from archivist.errors import (
    ArchivistBadRequestError,
    ArchivistHeaderError,
    ArchivistTooManyRequestsError,
)
from archivist.logger import set_logger
from archivist.archivistpublic import ArchivistPublic

from .mock_response import MockResponse


# pylint: disable=unused-variable
# pylint: disable=missing-docstring
# pylint: disable=protected-access

if "TEST_DEBUG" in environ and environ["TEST_DEBUG"]:
    set_logger(environ["TEST_DEBUG"])


class TestPublic(TestCase):
    """
    Test Public class
    """

    def test_public(self):
        """
        Test default public creation
        """
        public = ArchivistPublic()
        self.assertEqual(
            str(public),
            "ArchivistPublic()",
            msg="Incorrect str",
        )
        self.assertEqual(
            str(public.assets),
            "AssetsPublic()",
            msg="Incorrect assets",
        )
        self.assertEqual(
            str(public.events),
            "EventsPublic()",
            msg="Incorrect events",
        )
        self.assertEqual(
            public.verify,
            True,
            msg="verify must be True",
        )
        self.assertEqual(
            public.public,
            True,
            msg="verify must be True",
        )
        with self.assertRaises(AttributeError):
            e = public.Illegal_endpoint

    def test_public_copy(self):
        """
        Test public copy
        """
        public = ArchivistPublic(verify=False)
        public1 = copy(public)
        self.assertEqual(
            public.verify,
            public1.verify,
            msg="Incorrect verify",
        )
        self.assertEqual(
            public.fixtures,
            public1.fixtures,
            msg="Incorrect fixtures",
        )
        self.assertEqual(
            public.public,
            public1.public,
            msg="Incorrect public",
        )

    def test_public_no_verify(self):
        """
        Test public creation with no verify
        """
        public = ArchivistPublic(verify=False)
        self.assertFalse(
            public.verify,
            msg="verify must be False",
        )


class TestPublicMethods(TestCase):
    """
    Test Archivist base method class
    """

    def setUp(self):
        self.public = ArchivistPublic()


class TestPublicCount(TestPublicMethods):
    """
    Test Public count method
    """

    def test_count(self):
        """
        Test default count method
        """
        with mock.patch.object(self.public.session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                headers={HEADERS_TOTAL_COUNT.lower(): 1},
                things=[
                    {
                        "field1": "value1",
                    },
                ],
            )
            count = self.public.count("path/path")
            self.assertEqual(
                count,
                1,
                msg="incorrect count",
            )

    def test_count_with_error(self):
        """
        Test default count method with error
        """
        with mock.patch.object(self.public.session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                400,
                things=[
                    {
                        "field1": "value1",
                    },
                ],
            )
            with self.assertRaises(ArchivistBadRequestError):
                count = self.public.count("path/path")

    def test_count_with_missing_count_error(self):
        """
        Tests the default count method raises a ArchivistHeaderError when the
        expected count header field is missing
        """
        with mock.patch.object(self.public.session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                things=[
                    {
                        "field1": "value1",
                    },
                ],
            )
            with self.assertRaises(ArchivistHeaderError):
                count = self.public.count("path/path")

    def test_count_with_429(self):
        """
        Test count method with error
        """
        with mock.patch.object(self.public.session, "get") as mock_get:
            mock_get.return_value = MockResponse(429)
            with self.assertRaises(ArchivistTooManyRequestsError):
                count = self.public.count("path/path")

    def test_count_with_429_retry_and_fail(self):
        """
        Test count method with 429 retry and fail
        """
        with mock.patch.object(self.public.session, "get") as mock_get:
            mock_get.side_effect = (
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(429),
            )
            with self.assertRaises(ArchivistTooManyRequestsError):
                count = self.public.count("path/path")

    def test_count_with_429_retry_and_retries_fail(self):
        """
        Test count method with 429 retry and retries_fail
        """
        with mock.patch.object(self.public.session, "get") as mock_get:
            mock_get.side_effect = (
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
            )
            with self.assertRaises(ArchivistTooManyRequestsError):
                count = self.public.count("path/path")

    def test_count_with_429_retry_and_success(self):
        """
        Test count method with 429 retry and success
        """
        with mock.patch.object(self.public.session, "get") as mock_get:
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
            count = self.public.count("path/path")
            self.assertEqual(
                count,
                1,
                msg="incorrect count",
            )
