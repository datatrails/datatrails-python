"""
Test events confirm
"""

from unittest import TestCase, mock

from archivist.archivist import Archivist

from .mock_response import MockResponse
from .testeventsconstants import (
    ASSET_ID,
    EVENT_ATTRS,
    PROPS,
    RESPONSE,
    RESPONSE_PENDING,
)

# pylint: disable=missing-docstring
# pylint: disable=protected-access
# pylint: disable=unused-variable
# pylint: disable=too-many-public-methods


class TestEventsConfirm(TestCase):
    """
    Test Archivist Events Create method with expected confirm
    """

    maxDiff = None

    def setUp(self):
        self.arch = Archivist("url", "authauthauth", max_time=100)

    def tearDown(self):
        self.arch = None

    def test_events_create_with_confirmation(self):
        """
        Test event creation
        """
        with mock.patch.object(
            self.arch.session, "post"
        ) as mock_post, mock.patch.object(self.arch.session, "get") as mock_get:

            mock_post.return_value = MockResponse(200, **RESPONSE)
            mock_get.return_value = MockResponse(200, **RESPONSE)

            event = self.arch.events.create(ASSET_ID, PROPS, EVENT_ATTRS, confirm=True)
            self.assertEqual(
                event,
                RESPONSE,
                msg="CREATE method called incorrectly",
            )

    def test_events_create_with_confirmation_pending_status(self):
        """
        Test asset confirmation
        """
        with mock.patch.object(
            self.arch.session, "post"
        ) as mock_post, mock.patch.object(self.arch.session, "get") as mock_get:
            mock_post.return_value = MockResponse(200, **RESPONSE)
            mock_get.side_effect = [
                MockResponse(200, **RESPONSE_PENDING),
                MockResponse(200, **RESPONSE),
            ]
            event = self.arch.events.create(ASSET_ID, PROPS, EVENT_ATTRS, confirm=True)
            self.assertEqual(
                event,
                RESPONSE,
                msg="CREATE method called incorrectly",
            )
