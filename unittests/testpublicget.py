"""
Test public get
"""

from io import BytesIO
from unittest import TestCase, mock

from archivist.about import __version__ as VERSION
from archivist.archivistpublic import ArchivistPublic
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


class TestPublicMethods(TestCase):
    """
    Test Public base method class
    """

    def setUp(self):
        self.public = ArchivistPublic()

    def tearDown(self):
        self.public.close()


class TestPublicGet(TestPublicMethods):
    """
    Test Public Get method
    """

    def test_get(self):
        """
        Test default get method
        """
        with mock.patch.object(self.public.session, "get") as mock_get:
            mock_get.return_value = MockResponse(200)
            self.public.get("https://path/path/entity/xxxxxxxx")
            self.assertEqual(
                tuple(mock_get.call_args),
                (
                    ("https://path/path/entity/xxxxxxxx",),
                    {
                        "headers": {USER_AGENT: f"{USER_AGENT_PREFIX}{VERSION}"},
                        "params": None,
                    },
                ),
                msg="GET method called incorrectly",
            )

    def test_ring_buffer(self):
        """
        Test That the ring buffer for response objects works as expected
        """
        with mock.patch.object(self.public.session, "get") as mock_get:
            mock_get.return_value = MockResponse(200)
            self.public.get("https://path/path/entity/xxxxxxxx")
            last_response = self.public.last_response()
            self.assertEqual(last_response, [mock_get.return_value])

    def test_get_with_error(self):
        """
        Test get method with error
        """
        with mock.patch.object(self.public.session, "get") as mock_get:
            mock_get.return_value = MockResponse(404, identity="entity/xxxxxxxx")
            with self.assertRaises(ArchivistNotFoundError):
                self.public.get("https://path/path/entity/xxxxxxxx")

    def test_get_with_headers(self):
        """
        Test default get method
        """
        with mock.patch.object(self.public.session, "get") as mock_get:
            mock_get.return_value = MockResponse(200)
            self.public.get(
                "https://path/path/id/xxxxxxxx",
                headers={
                    "headerfield1": "headervalue1",
                    USER_AGENT: f"{USER_AGENT_PREFIX}{VERSION}",
                },
            )
            self.assertEqual(
                tuple(mock_get.call_args),
                (
                    ("https://path/path/id/xxxxxxxx",),
                    {
                        "headers": {
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
        with mock.patch.object(self.public.session, "get") as mock_get:
            mock_get.return_value = MockResponse(429)
            with self.assertRaises(ArchivistTooManyRequestsError):
                self.public.get(
                    "https://path/path/id/xxxxxxxx",
                    headers={
                        "headerfield1": "headervalue1",
                        USER_AGENT: f"{USER_AGENT_PREFIX}{VERSION}",
                    },
                )

    def test_get_with_429_retry_and_fail(self):
        """
        Test get method with 429 retry and fail
        """
        with mock.patch.object(self.public.session, "get") as mock_get:
            mock_get.side_effect = (
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(429),
            )
            with self.assertRaises(ArchivistTooManyRequestsError):
                self.public.get("https://path/path/entity/xxxxxxxx")

    def test_get_with_429_retry_and_retries_fail(self):
        """
        Test get method with 429 retry and retries_fail
        """
        with mock.patch.object(self.public.session, "get") as mock_get:
            mock_get.side_effect = (
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
            )
            with self.assertRaises(ArchivistTooManyRequestsError):
                self.public.get("https://path/path/entity/xxxxxxxx")

    def test_get_with_429_retry_and_success(self):
        """
        Test get method with 429 retry and success
        """
        with mock.patch.object(self.public.session, "get") as mock_get:
            mock_get.side_effect = (
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(200),
            )
            self.public.get("https://path/path/entity/xxxxxxxx")
            self.assertEqual(
                tuple(mock_get.call_args),
                (
                    ("https://path/path/entity/xxxxxxxx",),
                    {
                        "headers": {
                            USER_AGENT: f"{USER_AGENT_PREFIX}{VERSION}",
                        },
                        "params": None,
                    },
                ),
                msg="GET method called incorrectly",
            )


class TestPublicGetFile(TestPublicMethods):
    """
    Test Public Get method
    """

    def test_get_file(self):
        """
        Test default get method
        """

        with mock.patch.object(self.public.session, "get") as mock_get:

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
                self.public.get_file("https://path/path/entity/xxxxxxxx", fd)
                self.assertEqual(
                    tuple(mock_get.call_args),
                    (
                        ("https://path/path/entity/xxxxxxxx",),
                        {
                            "headers": {
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
        with mock.patch.object(self.public.session, "get") as mock_get:
            mock_get.return_value = MockResponse(404, identity="entity/xxxxxxxx")
            with self.assertRaises(ArchivistNotFoundError), BytesIO() as fd:
                self.public.get_file("https://path/path/entity/xxxxxxxx", fd)

    def test_get_file_with_429(self):
        """
        Test get method with error
        """
        with mock.patch.object(self.public.session, "get") as mock_get:
            mock_get.return_value = MockResponse(429)
            with self.assertRaises(ArchivistTooManyRequestsError), BytesIO() as fd:
                self.public.get_file("path/path/entity/xxxxxxxx", fd)

    def test_get_file_with_429_retry_and_fail(self):
        """
        Test get method with 429 retry and fail
        """
        with mock.patch.object(self.public.session, "get") as mock_get:
            mock_get.side_effect = (
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(429),
            )
            with self.assertRaises(ArchivistTooManyRequestsError), BytesIO() as fd:
                self.public.get_file("path/path/entity/xxxxxxxx", fd)

    def test_get_file_with_429_retry_and_retries_fail(self):
        """
        Test get method with 429 retry and retries_fail
        """
        with mock.patch.object(self.public.session, "get") as mock_get:
            mock_get.side_effect = (
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
            )
            with self.assertRaises(ArchivistTooManyRequestsError), BytesIO() as fd:
                self.public.get_file("path/path/entity/xxxxxxxx", fd)

    def test_get_file_with_429_retry_and_success(self):
        """
        Test get method with 429 retry and success
        """

        with mock.patch.object(self.public.session, "get") as mock_get:

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
                self.public.get_file("path/path/entity/xxxxxxxx", fd)
                self.assertEqual(
                    tuple(mock_get.call_args),
                    (
                        ("path/path/entity/xxxxxxxx",),
                        {
                            "headers": {
                                USER_AGENT: f"{USER_AGENT_PREFIX}{VERSION}",
                            },
                            "stream": True,
                            "params": None,
                        },
                    ),
                    msg="GET method called incorrectly",
                )
