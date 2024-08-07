"""
Test archivist signature
"""

from os import environ
from unittest import mock

from archivist.about import __version__ as VERSION
from archivist.constants import (
    USER_AGENT,
    USER_AGENT_PREFIX,
)
from archivist.errors import (
    ArchivistBadFieldError,
    ArchivistDuplicateError,
    ArchivistNotFoundError,
)
from archivist.logger import set_logger

from .mock_response import MockResponse
from .testarchivist import TestArchivistMethods

# pylint: disable=unused-variable
# pylint: disable=missing-docstring
# pylint: disable=protected-access

if "DATATRAILS_LOGLEVEL" in environ and environ["DATATRAILS_LOGLEVEL"]:
    set_logger(environ["DATATRAILS_LOGLEVEL"])


class TestArchivistSignature(TestArchivistMethods):
    """
    Test Archivist get_by_signature method
    """

    def test_get_by_signature(self):
        """
        Test default get_by_signature method
        """
        with mock.patch.object(self.arch.session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                things=[
                    {
                        "field1": "value1",
                    },
                ],
            )
            self.arch.get_by_signature("path/path", "things", {"field1": "value1"})
            for a in mock_get.call_args_list:
                self.assertEqual(
                    tuple(a),
                    (
                        ("path/path",),
                        {
                            "headers": {
                                "authorization": "Bearer authauthauth",
                                USER_AGENT: f"{USER_AGENT_PREFIX}{VERSION}",
                            },
                            "params": {"field1": "value1", "page_size": 2},
                        },
                    ),
                    msg="GET method called incorrectly",
                )

    def test_get_by_signature_not_found(self):
        """
        Test default get_by_signature method
        """
        with mock.patch.object(self.arch.session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                things=[],
            )
            with self.assertRaises(ArchivistNotFoundError):
                self.arch.get_by_signature("path/path", "things", {"field1": "value1"})

    def test_get_by_signature_duplicate(self):
        """
        Test default get_by_signature method
        """
        with mock.patch.object(self.arch.session, "get") as mock_get:
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
                self.arch.get_by_signature("path/path", "things", {"field1": "value1"})

    def test_get_by_signature_with_bad_field(self):
        """
        Test default list method with error
        """
        with mock.patch.object(self.arch.session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                things=[
                    {
                        "field1": "value1",
                    },
                ],
            )
            with self.assertRaises(ArchivistBadFieldError):
                self.arch.get_by_signature(
                    "path/path", "badthings", {"field1": "value1"}
                )
