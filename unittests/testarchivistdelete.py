"""
Test archivist delete
"""

from unittest import TestCase, mock

from archivist.about import __version__ as VERSION
from archivist.archivist import Archivist
from archivist.constants import (
    HEADERS_RETRY_AFTER,
    USER_AGENT,
    USER_AGENT_PREFIX,
)
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
        self.arch = Archivist("url", "authauthauth")

    def tearDown(self):
        self.arch.close()


class TestArchivistDelete(TestArchivistMethods):
    """
    Test Archivist Delete method
    """

    def test_delete(self):
        """
        Test default delete method
        """
        with mock.patch.object(self.arch.session, "delete") as mock_delete:
            mock_delete.return_value = MockResponse(200)
            self.arch.delete("path/path/entity/xxxxxxxx")
            self.assertEqual(
                tuple(mock_delete.call_args),
                (
                    ("path/path/entity/xxxxxxxx",),
                    {
                        "headers": {
                            "authorization": "Bearer authauthauth",
                            USER_AGENT: f"{USER_AGENT_PREFIX}{VERSION}",
                        },
                    },
                ),
                msg="DELETE method called incorrectly",
            )

    def test_delete_with_error(self):
        """
        Test delete method with error
        """
        with mock.patch.object(self.arch.session, "delete") as mock_delete:
            mock_delete.return_value = MockResponse(404, identity="entity/xxxxxxxx")
            with self.assertRaises(ArchivistNotFoundError):
                self.arch.delete("path/path/entity/xxxxxxxx")

    def test_delete_with_headers(self):
        """
        Test default delete method
        """
        with mock.patch.object(self.arch.session, "delete") as mock_delete:
            mock_delete.return_value = MockResponse(200)
            self.arch.delete(
                "path/path/id/xxxxxxxx",
                headers={
                    "headerfield1": "headervalue1",
                    USER_AGENT: f"{USER_AGENT_PREFIX}{VERSION}",
                },
            )
            self.assertEqual(
                tuple(mock_delete.call_args),
                (
                    ("path/path/id/xxxxxxxx",),
                    {
                        "headers": {
                            "authorization": "Bearer authauthauth",
                            "headerfield1": "headervalue1",
                            USER_AGENT: f"{USER_AGENT_PREFIX}{VERSION}",
                        },
                    },
                ),
                msg="DELETE method called incorrectly",
            )

    def test_delete_with_429(self):
        """
        Test delete method with error
        """
        with mock.patch.object(self.arch.session, "delete") as mock_delete:
            mock_delete.return_value = MockResponse(429)
            with self.assertRaises(ArchivistTooManyRequestsError):
                self.arch.delete(
                    "path/path/id/xxxxxxxx",
                    headers={
                        "headerfield1": "headervalue1",
                        USER_AGENT: f"{USER_AGENT_PREFIX}{VERSION}",
                    },
                )

    def test_delete_with_429_retry_and_fail(self):
        """
        Test delete method with 429 retry and fail
        """
        with mock.patch.object(self.arch.session, "delete") as mock_delete:
            mock_delete.side_effect = (
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(429),
            )
            with self.assertRaises(ArchivistTooManyRequestsError):
                self.arch.delete("path/path/entity/xxxxxxxx")

    def test_delete_with_429_retry_and_retries_fail(self):
        """
        Test delete method with 429 retry and retries_fail
        """
        with mock.patch.object(self.arch.session, "delete") as mock_delete:
            mock_delete.side_effect = (
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
            )
            with self.assertRaises(ArchivistTooManyRequestsError):
                self.arch.delete("path/path/entity/xxxxxxxx")

    def test_delete_with_429_retry_and_success(self):
        """
        Test delete method with 429 retry and success
        """
        with mock.patch.object(self.arch.session, "delete") as mock_delete:
            mock_delete.side_effect = (
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(200),
            )
            self.arch.delete("path/path/entity/xxxxxxxx")
            self.assertEqual(
                tuple(mock_delete.call_args),
                (
                    ("path/path/entity/xxxxxxxx",),
                    {
                        "headers": {
                            "authorization": "Bearer authauthauth",
                            USER_AGENT: f"{USER_AGENT_PREFIX}{VERSION}",
                        },
                    },
                ),
                msg="DELETE method called incorrectly",
            )
