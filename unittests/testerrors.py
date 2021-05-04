"""
Test archivist
"""

# pylint: disable=attribute-defined-outside-init
# pylint: disable=missing-docstring
# pylint: disable=too-few-public-methods

import json

from unittest import TestCase

from archivist.errors import (
    parse_response,
    Archivist4xxError,
    Archivist5xxError,
    ArchivistBadRequestError,
    ArchivistError,
    ArchivistForbiddenError,
    ArchivistNotFoundError,
    ArchivistNotImplementedError,
    ArchivistUnauthenticatedError,
    ArchivistUnavailableError,
)

from .mock_response import MockResponse


class TestErrors(TestCase):
    """
    Test exceptions for archivist
    """

    def test_errors_200(self):
        """
        Test errors
        """
        response = MockResponse(200)
        error = parse_response(response)
        self.assertEqual(
            error,
            None,
            msg="error should be None",
        )

    def test_errors_300(self):
        """
        Test errors
        """
        response = MockResponse(300)
        error = parse_response(response)
        self.assertEqual(
            error,
            None,
            msg="error should be None",
        )

    def test_errors_400(self):
        """
        Test errors
        """
        response = MockResponse(400, error="some error")
        error = parse_response(response)
        self.assertIsNotNone(
            error,
            msg="error should not be None",
        )
        with self.assertRaises(ArchivistBadRequestError) as ex:
            raise error
        self.assertEqual(
            str(ex.exception),
            '{"error": "some error"} (400)',
            msg="incorrect error",
        )

    def test_errors_401(self):
        """
        Test errors
        """
        response = MockResponse(401, error="some error")
        error = parse_response(response)
        self.assertIsNotNone(
            error,
            msg="error should not be None",
        )
        with self.assertRaises(ArchivistUnauthenticatedError) as ex:
            raise error
        self.assertEqual(
            str(ex.exception),
            '{"error": "some error"} (401)',
            msg="incorrect error",
        )

    def test_errors_403(self):
        """
        Test errors
        """
        response = MockResponse(403, error="some error")
        error = parse_response(response)
        self.assertIsNotNone(
            error,
            msg="error should not be None",
        )
        with self.assertRaises(ArchivistForbiddenError) as ex:
            raise error
        self.assertEqual(
            str(ex.exception),
            '{"error": "some error"} (403)',
        )

    def test_errors_404(self):
        """
        Test errors
        """

        class Object:
            pass

        request = Object()
        request.body = json.dumps({"identity": "entity/xxxxx"})
        response = MockResponse(
            404,
            request=request,
            error="some error",
        )
        error = parse_response(response)
        self.assertIsNotNone(
            error,
            msg="error should not be None",
        )
        with self.assertRaises(ArchivistNotFoundError) as ex:
            raise error
        self.assertEqual(
            str(ex.exception),
            "entity/xxxxx not found (404)",
            msg="incorrect error",
        )

    def test_errors_4xx(self):
        """
        Test errors
        """
        response = MockResponse(405, error="some error")
        error = parse_response(response)
        self.assertIsNotNone(
            error,
            msg="error should not be None",
        )
        with self.assertRaises(Archivist4xxError) as ex:
            raise error
        self.assertEqual(
            str(ex.exception),
            '{"error": "some error"} (405)',
            msg="incorrect error",
        )

    def test_errors_500(self):
        """
        Test errors
        """
        response = MockResponse(500, error="some error")
        error = parse_response(response)
        self.assertIsNotNone(
            error,
            msg="error should not be None",
        )
        with self.assertRaises(Archivist5xxError) as ex:
            raise error
        self.assertEqual(
            str(ex.exception),
            '{"error": "some error"} (500)',
            msg="incorrect error",
        )

    def test_errors_501(self):
        """
        Test errors
        """
        response = MockResponse(501, error="some error")
        error = parse_response(response)
        self.assertIsNotNone(
            error,
            msg="error should not be None",
        )
        with self.assertRaises(ArchivistNotImplementedError) as ex:
            raise error
        self.assertEqual(
            str(ex.exception),
            '{"error": "some error"} (501)',
            msg="incorrect error",
        )

    def test_errors_503(self):
        """
        Test errors
        """
        response = MockResponse(503, error="some error")
        error = parse_response(response)
        self.assertIsNotNone(
            error,
            msg="error should not be None",
        )
        with self.assertRaises(ArchivistUnavailableError) as ex:
            raise error
        self.assertEqual(
            str(ex.exception),
            '{"error": "some error"} (503)',
            msg="incorrect error",
        )

    def test_errors_600(self):
        """
        Test errors
        """
        response = MockResponse(600, error="some error")
        error = parse_response(response)
        self.assertIsNotNone(
            error,
            msg="error should not be None",
        )
        with self.assertRaises(ArchivistError) as ex:
            raise error
        self.assertEqual(
            str(ex.exception),
            '{"error": "some error"} (600)',
            msg="incorrect error",
        )
