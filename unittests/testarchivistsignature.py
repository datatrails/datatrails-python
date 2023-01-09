"""
Test archivist signature
"""

from os import environ
from unittest import mock

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

if "RKVST_DEBUG" in environ and environ["RKVST_DEBUG"]:
    set_logger(environ["RKVST_DEBUG"])


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
            entity = self.arch.get_by_signature(
                "path/path", "things", {"field1": "value1"}
            )
            for a in mock_get.call_args_list:
                self.assertEqual(
                    tuple(a),
                    (
                        ("path/path",),
                        {
                            "headers": {
                                "authorization": "Bearer authauthauth",
                            },
                            "params": {"field1": "value1", "page_size": 2},
                            "verify": True,
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
                entity = self.arch.get_by_signature(
                    "path/path", "things", {"field1": "value1"}
                )

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
                entity = self.arch.get_by_signature(
                    "path/path", "things", {"field1": "value1"}
                )

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
                entity = self.arch.get_by_signature(
                    "path/path", "badthings", {"field1": "value1"}
                )
