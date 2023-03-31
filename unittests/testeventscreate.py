"""
Test events create
"""

from unittest import mock

from archivist.constants import (
    ASSETS_LABEL,
    ASSETS_SUBPATH,
    EVENTS_LABEL,
    ROOT,
)
from archivist.errors import (
    ArchivistUnconfirmedError,
)

from .mock_response import MockResponse
from .testeventsconstants import (
    ASSET_ATTRS,
    ASSET_ID,
    ATTACHMENTS,
    EVENT_ATTRS,
    EVENT_ATTRS_ATTACHMENTS,
    EVENT_ATTRS_LOCATION,
    EVENT_ATTRS_LOCATION_IDENTITY,
    EVENT_ATTRS_SBOMATTACHMENT,
    LOCATION,
    PROPS,
    REQUEST,
    REQUEST_WITH_ASSET_ATTRS,
    REQUEST_WITH_ATTACHMENTS,
    REQUEST_WITH_LOCATION,
    REQUEST_WITH_SBOMATTACHMENT,
    RESPONSE,
    RESPONSE_FAILED,
    RESPONSE_NO_CONFIRMATION,
    RESPONSE_PENDING,
    RESPONSE_WITH_ASSET_ATTRS,
    RESPONSE_WITH_ATTACHMENTS,
    RESPONSE_WITH_LOCATION,
    RESPONSE_WITH_SBOMATTACHMENT,
    SBOM_RESULT,
    TestEventsBase,
)

# pylint: disable=missing-docstring
# pylint: disable=protected-access
# pylint: disable=unused-variable
# pylint: disable=too-many-public-methods


class TestEventsCreate(TestEventsBase):
    """
    Test Archivist Events Create method
    """

    def test_events_str(self):
        """
        Test events str
        """
        self.assertEqual(
            str(self.arch.events),
            "EventsRestricted(url)",
            msg="Incorrect str",
        )

    def test_events_create(self):
        """
        Test event creation
        """
        with mock.patch.object(self.arch.session, "post") as mock_post:
            mock_post.return_value = MockResponse(200, **RESPONSE)

            event = self.arch.events.create(ASSET_ID, PROPS, EVENT_ATTRS, confirm=False)
            args, kwargs = mock_post.call_args
            self.assertEqual(
                args,
                (
                    (
                        f"url/{ROOT}/{ASSETS_SUBPATH}"
                        f"/{ASSETS_LABEL}/xxxxxxxxxxxxxxxxxxxx"
                        f"/{EVENTS_LABEL}"
                    ),
                ),
                msg="CREATE method args called incorrectly",
            )
            self.assertEqual(
                kwargs,
                {
                    "json": REQUEST,
                    "headers": {
                        "authorization": "Bearer authauthauth",
                    },
                    "verify": True,
                },
                msg="CREATE method kwargs called incorrectly",
            )
            self.assertEqual(
                event,
                RESPONSE,
                msg="CREATE method called incorrectly",
            )

    def test_events_create_with_upload_attachments(self):
        """
        Test event creation
        """
        with mock.patch.object(
            self.arch.session, "post"
        ) as mock_post, mock.patch.object(
            self.arch.attachments, "create"
        ) as mock_attachments_create:
            mock_post.return_value = MockResponse(200, **RESPONSE_WITH_ATTACHMENTS)
            mock_attachments_create.return_value = ATTACHMENTS

            event = self.arch.events.create_from_data(
                ASSET_ID, EVENT_ATTRS_ATTACHMENTS, confirm=False
            )
            args, kwargs = mock_post.call_args
            self.assertEqual(
                args,
                (
                    (
                        f"url/{ROOT}/{ASSETS_SUBPATH}"
                        f"/{ASSETS_LABEL}/xxxxxxxxxxxxxxxxxxxx"
                        f"/{EVENTS_LABEL}"
                    ),
                ),
                msg="CREATE method args called incorrectly",
            )
            self.assertEqual(
                kwargs,
                {
                    "json": REQUEST_WITH_ATTACHMENTS,
                    "headers": {
                        "authorization": "Bearer authauthauth",
                    },
                    "verify": True,
                },
                msg="CREATE method kwargs called incorrectly",
            )
            self.assertEqual(
                event,
                RESPONSE_WITH_ATTACHMENTS,
                msg="CREATE method called incorrectly",
            )

    def test_events_create_with_upload_sbom_as_attachment(self):
        """
        Test event creation
        """
        with mock.patch.object(
            self.arch.session, "post"
        ) as mock_post, mock.patch.object(
            self.arch.attachments, "create"
        ) as mock_attachments_create, mock.patch(
            "archivist.events.sboms_parse"
        ) as mock_sboms_parse:
            mock_post.return_value = MockResponse(200, **RESPONSE_WITH_SBOMATTACHMENT)
            mock_sboms_parse.return_value = SBOM_RESULT
            mock_attachments_create.return_value = ATTACHMENTS

            event = self.arch.events.create_from_data(
                ASSET_ID, EVENT_ATTRS_SBOMATTACHMENT, confirm=False
            )
            args, kwargs = mock_post.call_args
            self.assertEqual(
                args,
                (
                    (
                        f"url/{ROOT}/{ASSETS_SUBPATH}"
                        f"/{ASSETS_LABEL}/xxxxxxxxxxxxxxxxxxxx"
                        f"/{EVENTS_LABEL}"
                    ),
                ),
                msg="CREATE method args called incorrectly",
            )
            self.assertEqual(
                kwargs,
                {
                    "json": REQUEST_WITH_SBOMATTACHMENT,
                    "headers": {
                        "authorization": "Bearer authauthauth",
                    },
                    "verify": True,
                },
                msg="CREATE method kwargs called incorrectly",
            )
            self.assertEqual(
                event,
                RESPONSE_WITH_SBOMATTACHMENT,
                msg="CREATE method called incorrectly",
            )

    def test_events_create_with_location(self):
        """
        Test event creation
        """
        with mock.patch.object(
            self.arch.session, "post"
        ) as mock_post, mock.patch.object(
            self.arch.locations, "create_if_not_exists"
        ) as mock_location_create:
            mock_post.return_value = MockResponse(200, **RESPONSE_WITH_LOCATION)
            mock_location_create.return_value = LOCATION, True

            event = self.arch.events.create_from_data(
                ASSET_ID, EVENT_ATTRS_LOCATION, confirm=False
            )
            args, kwargs = mock_post.call_args
            self.assertEqual(
                args,
                (
                    (
                        f"url/{ROOT}/{ASSETS_SUBPATH}"
                        f"/{ASSETS_LABEL}/xxxxxxxxxxxxxxxxxxxx"
                        f"/{EVENTS_LABEL}"
                    ),
                ),
                msg="CREATE method args called incorrectly",
            )
            self.assertEqual(
                kwargs,
                {
                    "json": REQUEST_WITH_LOCATION,
                    "headers": {
                        "authorization": "Bearer authauthauth",
                    },
                    "verify": True,
                },
                msg="CREATE method kwargs called incorrectly",
            )
            self.assertEqual(
                event,
                RESPONSE_WITH_LOCATION,
                msg="CREATE method called incorrectly",
            )

    def test_events_create_with_location_identity(self):
        """
        Test event creation
        """
        with mock.patch.object(
            self.arch.session, "post"
        ) as mock_post, mock.patch.object(self.arch.locations, "create_if_not_exists"):
            mock_post.return_value = MockResponse(200, **RESPONSE_WITH_LOCATION)

            event = self.arch.events.create_from_data(
                ASSET_ID, EVENT_ATTRS_LOCATION_IDENTITY, confirm=False
            )
            args, kwargs = mock_post.call_args
            self.assertEqual(
                args,
                (
                    (
                        f"url/{ROOT}/{ASSETS_SUBPATH}"
                        f"/{ASSETS_LABEL}/xxxxxxxxxxxxxxxxxxxx"
                        f"/{EVENTS_LABEL}"
                    ),
                ),
                msg="CREATE method args called incorrectly",
            )
            self.assertEqual(
                kwargs,
                {
                    "json": REQUEST_WITH_LOCATION,
                    "headers": {
                        "authorization": "Bearer authauthauth",
                    },
                    "verify": True,
                },
                msg="CREATE method kwargs called incorrectly",
            )
            self.assertEqual(
                event,
                RESPONSE_WITH_LOCATION,
                msg="CREATE method called incorrectly",
            )

    def test_events_create_with_asset_attrs(self):
        """
        Test event creation
        """
        with mock.patch.object(self.arch.session, "post") as mock_post:
            mock_post.return_value = MockResponse(200, **RESPONSE_WITH_ASSET_ATTRS)

            event = self.arch.events.create(
                ASSET_ID,
                PROPS,
                EVENT_ATTRS,
                asset_attrs=ASSET_ATTRS,
                confirm=False,
            )
            args, kwargs = mock_post.call_args
            self.assertEqual(
                args,
                (
                    (
                        f"url/{ROOT}/{ASSETS_SUBPATH}"
                        f"/{ASSETS_LABEL}/xxxxxxxxxxxxxxxxxxxx"
                        f"/{EVENTS_LABEL}"
                    ),
                ),
                msg="CREATE method args called incorrectly",
            )
            self.assertEqual(
                kwargs,
                {
                    "json": REQUEST_WITH_ASSET_ATTRS,
                    "headers": {
                        "authorization": "Bearer authauthauth",
                    },
                    "verify": True,
                },
                msg="CREATE method kwargs called incorrectly",
            )
            self.assertEqual(
                event,
                RESPONSE_WITH_ASSET_ATTRS,
                msg="CREATE method called incorrectly",
            )

    def test_events_create_with_explicit_confirmation(self):
        """
        Test event creation
        """
        with mock.patch.object(
            self.arch.session, "post"
        ) as mock_post, mock.patch.object(self.arch.session, "get") as mock_get:
            mock_post.return_value = MockResponse(200, **RESPONSE)
            mock_get.return_value = MockResponse(200, **RESPONSE)

            event = self.arch.events.create(ASSET_ID, PROPS, EVENT_ATTRS, confirm=False)
            self.arch.events.wait_for_confirmation(event["identity"])
            self.assertEqual(
                event,
                RESPONSE,
                msg="CREATE method called incorrectly",
            )

    def test_events_create_with_confirmation_no_confirmed_status(self):
        """
        Test asset confirmation
        """
        with mock.patch.object(
            self.arch.session, "post"
        ) as mock_post, mock.patch.object(self.arch.session, "get") as mock_get:
            mock_post.return_value = MockResponse(200, **RESPONSE)
            mock_get.return_value = MockResponse(200, **RESPONSE_NO_CONFIRMATION)

            with self.assertRaises(ArchivistUnconfirmedError):
                self.arch.events.create(ASSET_ID, PROPS, EVENT_ATTRS, confirm=True)

    def test_events_create_with_confirmation_failed_status(self):
        """
        Test asset confirmation
        """
        with mock.patch.object(
            self.arch.session, "post"
        ) as mock_post, mock.patch.object(self.arch.session, "get") as mock_get:
            mock_post.return_value = MockResponse(200, **RESPONSE)
            mock_get.side_effect = [
                MockResponse(200, **RESPONSE_PENDING),
                MockResponse(200, **RESPONSE_FAILED),
            ]
            with self.assertRaises(ArchivistUnconfirmedError):
                self.arch.events.create(ASSET_ID, PROPS, EVENT_ATTRS, confirm=True)

    def test_events_create_with_confirmation_always_pending_status(self):
        """
        Test asset confirmation
        """
        with mock.patch.object(
            self.arch.session, "post"
        ) as mock_post, mock.patch.object(self.arch.session, "get") as mock_get:
            mock_post.return_value = MockResponse(200, **RESPONSE)
            mock_get.side_effect = [
                MockResponse(200, **RESPONSE_PENDING),
                MockResponse(200, **RESPONSE_PENDING),
                MockResponse(200, **RESPONSE_PENDING),
                MockResponse(200, **RESPONSE_PENDING),
                MockResponse(200, **RESPONSE_PENDING),
                MockResponse(200, **RESPONSE_PENDING),
                MockResponse(200, **RESPONSE_PENDING),
            ]

            with self.assertRaises(ArchivistUnconfirmedError):
                self.arch.events.create(ASSET_ID, PROPS, EVENT_ATTRS, confirm=True)
