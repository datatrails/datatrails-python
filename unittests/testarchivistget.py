"""
Test archivist get
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


class TestArchivistGet(TestArchivistMethods):
    """
    Test Archivist Get method
    """

    def test_get(self):
        """
        Test default get method
        """
        with mock.patch.object(self.arch.session, "get") as mock_get:
            mock_get.return_value = MockResponse(200)
            self.arch.get("path/path/entity/xxxxxxxx")
            self.assertEqual(
                tuple(mock_get.call_args),
                (
                    ("path/path/entity/xxxxxxxx",),
                    {
                        "headers": {
                            "authorization": "Bearer authauthauth",
                            USER_AGENT: f"{USER_AGENT_PREFIX}{VERSION}",
                        },
                        "params": None,
                    },
                ),
                msg="GET method called incorrectly",
            )

    def test_get_binary(self):
        """
        Test default get_binary method
        """
        content = bytearray()
        content.extend(b"response")
        with mock.patch.object(self.arch.session, "get") as mock_get:
            mock_get.return_value = MockResponse(200, content=content)
            result = self.arch.get_binary("path/path/entity/xxxxxxxx")
            self.assertEqual(
                tuple(mock_get.call_args),
                (
                    ("path/path/entity/xxxxxxxx",),
                    {
                        "headers": {
                            "authorization": "Bearer authauthauth",
                            USER_AGENT: f"{USER_AGENT_PREFIX}{VERSION}",
                        },
                        "params": None,
                    },
                ),
                msg="GET method called incorrectly",
            )
            self.assertEqual(
                result,
                content,
                msg="GET result is incorrect",
            )

    def test_ring_buffer(self):
        """
        Test That the ring buffer for response objects works as expected
        """
        with mock.patch.object(self.arch.session, "get") as mock_get:
            mock_get.return_value = MockResponse(200)
            self.arch.get("path/path/entity/xxxxxxxx")
            last_response = self.arch.last_response()
            self.assertEqual(last_response, [mock_get.return_value])

    def test_get_with_error(self):
        """
        Test get method with error
        """
        with mock.patch.object(self.arch.session, "get") as mock_get:
            mock_get.return_value = MockResponse(404, identity="entity/xxxxxxxx")
            with self.assertRaises(ArchivistNotFoundError):
                self.arch.get("path/path/entity/xxxxxxxx")

    def test_get_with_headers(self):
        """
        Test default get method
        """
        with mock.patch.object(self.arch.session, "get") as mock_get:
            mock_get.return_value = MockResponse(200)
            self.arch.get(
                "path/path/id/xxxxxxxx",
                headers={
                    "headerfield1": "headervalue1",
                    USER_AGENT: f"{USER_AGENT_PREFIX}{VERSION}",
                },
            )
            self.assertEqual(
                tuple(mock_get.call_args),
                (
                    ("path/path/id/xxxxxxxx",),
                    {
                        "headers": {
                            "authorization": "Bearer authauthauth",
                            "headerfield1": "headervalue1",
                            USER_AGENT: f"{USER_AGENT_PREFIX}{VERSION}",
                        },
                        "params": None,
                    },
                ),
                msg="GET method called incorrectly",
            )

    def test_get_with_429(self):
        """
        Test get method with error
        """
        with mock.patch.object(self.arch.session, "get") as mock_get:
            mock_get.return_value = MockResponse(429)
            with self.assertRaises(ArchivistTooManyRequestsError):
                self.arch.get(
                    "path/path/id/xxxxxxxx",
                    headers={
                        "headerfield1": "headervalue1",
                        USER_AGENT: f"{USER_AGENT_PREFIX}{VERSION}",
                    },
                )

    def test_get_with_429_retry_and_fail(self):
        """
        Test get method with 429 retry and fail
        """
        with mock.patch.object(self.arch.session, "get") as mock_get:
            mock_get.side_effect = (
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(429),
            )
            with self.assertRaises(ArchivistTooManyRequestsError):
                self.arch.get("path/path/entity/xxxxxxxx")

    def test_get_with_429_retry_and_retries_fail(self):
        """
        Test get method with 429 retry and retries_fail
        """
        with mock.patch.object(self.arch.session, "get") as mock_get:
            mock_get.side_effect = (
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
            )
            with self.assertRaises(ArchivistTooManyRequestsError):
                self.arch.get("path/path/entity/xxxxxxxx")

    def test_get_with_429_retry_and_success(self):
        """
        Test get method with 429 retry and success
        """
        with mock.patch.object(self.arch.session, "get") as mock_get:
            mock_get.side_effect = (
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(200),
            )
            self.arch.get("path/path/entity/xxxxxxxx")
            self.assertEqual(
                tuple(mock_get.call_args),
                (
                    ("path/path/entity/xxxxxxxx",),
                    {
                        "headers": {
                            "authorization": "Bearer authauthauth",
                            USER_AGENT: f"{USER_AGENT_PREFIX}{VERSION}",
                        },
                        "params": None,
                    },
                ),
                msg="GET method called incorrectly",
            )


class TestArchivistGetFile(TestArchivistMethods):
    """
    Test Archivist Get method
    """

    def test_get_file(self):
        """
        Test default get method
        """

        with mock.patch.object(self.arch.session, "get") as mock_get:

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
                self.arch.get_file("path/path/entity/xxxxxxxx", fd)
                self.assertEqual(
                    tuple(mock_get.call_args),
                    (
                        ("path/path/entity/xxxxxxxx",),
                        {
                            "headers": {
                                "authorization": "Bearer authauthauth",
                                USER_AGENT: f"{USER_AGENT_PREFIX}{VERSION}",
                            },
                            "stream": True,
                            "params": None,
                        },
                    ),
                    msg="GET method called incorrectly",
                )

    def test_get_file_with_error(self):
        """
        Test get method with error
        """
        with mock.patch.object(self.arch.session, "get") as mock_get:
            mock_get.return_value = MockResponse(404, identity="entity/xxxxxxxx")
            with self.assertRaises(ArchivistNotFoundError), BytesIO() as fd:
                self.arch.get_file("path/path/entity/xxxxxxxx", fd)

    def test_get_file_with_429(self):
        """
        Test get method with error
        """
        with mock.patch.object(self.arch.session, "get") as mock_get:
            mock_get.return_value = MockResponse(429)
            with self.assertRaises(ArchivistTooManyRequestsError), BytesIO() as fd:
                self.arch.get_file("path/path/entity/xxxxxxxx", fd)

    def test_get_file_with_429_retry_and_fail(self):
        """
        Test get method with 429 retry and fail
        """
        with mock.patch.object(self.arch.session, "get") as mock_get:
            mock_get.side_effect = (
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(429),
            )
            with self.assertRaises(ArchivistTooManyRequestsError), BytesIO() as fd:
                self.arch.get_file("path/path/entity/xxxxxxxx", fd)

    def test_get_file_with_429_retry_and_retries_fail(self):
        """
        Test get method with 429 retry and retries_fail
        """
        with mock.patch.object(self.arch.session, "get") as mock_get:
            mock_get.side_effect = (
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
            )
            with self.assertRaises(ArchivistTooManyRequestsError), BytesIO() as fd:
                self.arch.get_file("path/path/entity/xxxxxxxx", fd)

    def test_get_file_with_429_retry_and_success(self):
        """
        Test get method with 429 retry and success
        """

        with mock.patch.object(self.arch.session, "get") as mock_get:

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

            mock_get.side_effect = (
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(
                    200,
                    identity="entity/xxxxxxxx",
                    iter_content=iter_content(),
                ),
            )
            with BytesIO() as fd:
                self.arch.get_file("path/path/entity/xxxxxxxx", fd)
                self.assertEqual(
                    tuple(mock_get.call_args),
                    (
                        ("path/path/entity/xxxxxxxx",),
                        {
                            "headers": {
                                "authorization": "Bearer authauthauth",
                                USER_AGENT: f"{USER_AGENT_PREFIX}{VERSION}",
                            },
                            "stream": True,
                            "params": None,
                        },
                    ),
                    msg="GET method called incorrectly",
                )
