"""
Test archivist
"""

from unittest import TestCase, mock

from archivist.archivist import Archivist
from archivist.constants import ROOT, HEADERS_RETRY_AFTER
from archivist.errors import (
    ArchivistNotFoundError,
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
        self.arch = Archivist("url", auth="authauthauth")


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

    def test_delete_with_429(self):
        """
        Test delete method with error
        """
        with mock.patch.object(self.arch._session, "delete") as mock_delete:
            mock_delete.return_value = MockResponse(429)
            with self.assertRaises(ArchivistTooManyRequestsError):
                resp = self.arch.delete(
                    "path/path",
                    "id/xxxxxxxx",
                    headers={"headerfield1": "headervalue1"},
                )

    def test_delete_with_429_retry_and_fail(self):
        """
        Test delete method with 429 retry and fail
        """
        with mock.patch.object(self.arch._session, "delete") as mock_delete:
            mock_delete.side_effect = (
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(429),
            )
            with self.assertRaises(ArchivistTooManyRequestsError):
                resp = self.arch.delete("path/path", "entity/xxxxxxxx")

    def test_delete_with_429_retry_and_retries_fail(self):
        """
        Test delete method with 429 retry and retries_fail
        """
        with mock.patch.object(self.arch._session, "delete") as mock_delete:
            mock_delete.side_effect = (
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
            )
            with self.assertRaises(ArchivistTooManyRequestsError):
                resp = self.arch.delete("path/path", "entity/xxxxxxxx")

    def test_delete_with_429_retry_and_success(self):
        """
        Test delete method with 429 retry and success
        """
        with mock.patch.object(self.arch._session, "delete") as mock_delete:
            mock_delete.side_effect = (
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(200),
            )
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
