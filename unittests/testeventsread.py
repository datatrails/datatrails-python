"""
Test events read
"""

from unittest import mock

from archivist.constants import (
    ASSETS_LABEL,
    ASSETS_SUBPATH,
    EVENTS_LABEL,
    ROOT,
)
from archivist.errors import ArchivistBadFieldError

from .mock_response import MockResponse
from .testeventsconstants import (
    IDENTITY,
    PUBLICURL,
    RESPONSE,
    RESPONSE_BAD_PUBLICURL,
    RESPONSE_PUBLICURL,
    TestEventsBase,
)

# pylint: disable=missing-docstring
# pylint: disable=protected-access
# pylint: disable=unused-variable
# pylint: disable=too-many-public-methods


class TestEventsRead(TestEventsBase):
    """
    Test Archivist Events Read method
    """

    def test_events_read(self):
        """
        Test event reading
        """
        with mock.patch.object(self.arch.session, "get") as mock_get:
            mock_get.return_value = MockResponse(200, **RESPONSE)

            event = self.arch.events.read(IDENTITY)
            self.assertEqual(
                tuple(mock_get.call_args),
                (
                    (
                        (
                            f"url/{ROOT}/{ASSETS_SUBPATH}"
                            f"/{ASSETS_LABEL}/xxxxxxxxxxxxxxxxxxxx"
                            f"/{EVENTS_LABEL}/xxxxxxxxxxxxxxxxxxxx"
                        ),
                    ),
                    {
                        "headers": {
                            "authorization": "Bearer authauthauth",
                        },
                        "params": None,
                    },
                ),
                msg="GET method called incorrectly",
            )
            self.assertEqual(
                event,
                RESPONSE,
                msg="GET method called incorrectly",
            )

    def test_events_read_with_no_principal(self):
        """
        Test event reading
        """
        with mock.patch.object(self.arch.session, "get") as mock_get:
            mock_get.return_value = MockResponse(200, **RESPONSE)

            event = self.arch.events.read(IDENTITY)
            self.assertEqual(
                event,
                RESPONSE,
                msg="GET method called incorrectly",
            )

    def test_events_publicurl(self):
        """
        Test event reading publicurl
        """
        with mock.patch.object(self.arch.session, "get") as mock_get:
            mock_get.return_value = MockResponse(200, **RESPONSE_PUBLICURL)

            publicurl = self.arch.events.publicurl(IDENTITY)
            self.assertEqual(
                publicurl,
                PUBLICURL,
                msg="Public url is incorrect",
            )

    def test_events_publicurl_bad_response(self):
        """
        Test event reading publicurl with bad response
        """
        with mock.patch.object(self.arch.session, "get") as mock_get:
            mock_get.return_value = MockResponse(200, **RESPONSE_BAD_PUBLICURL)

            with self.assertRaises(ArchivistBadFieldError):
                self.arch.events.publicurl(IDENTITY)
