"""
Test archivist
"""

from unittest import TestCase, mock

from archivist.archivist import Archivist
from archivist.constants import (
    ROOT,
    ASSETS_LABEL,
    ASSETS_WILDCARD,
    ASSETS_SUBPATH,
    ATTACHMENTS_LABEL,
    EVENTS_LABEL,
    HEADERS_REQUEST_TOTAL_COUNT,
    HEADERS_TOTAL_COUNT,
    SBOM_RELEASE,
)
from archivist.errors import ArchivistNotFoundError, ArchivistUnconfirmedError
from archivist.events import Event

from .mock_response import MockResponse

# pylint: disable=missing-docstring
# pylint: disable=protected-access
# pylint: disable=unused-variable
# pylint: disable=too-many-lines
# pylint: disable=too-many-public-methods

ASSET_ID = f"{ASSETS_LABEL}/xxxxxxxxxxxxxxxxxxxx"

PRIMARY_IMAGE = {
    "arc_attachment_identity": f"{ATTACHMENTS_LABEL}/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "arc_display_name": "an attachment 2",
    "arc_hash_value": "042aea10a0f14f2d391373599be69d53a75dde9951fc3d3cd10b6100aa7a9f24",
    "arc_hash_alg": "sha256",
}
SECONDARY_IMAGE = {
    "arc_attachment_identity": f"{ATTACHMENTS_LABEL}/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "arc_display_name": "an attachment 1",
    "arc_hash_value": "jnwpjocoqsssnundwlqalsqiiqsqp;lpiwpldkndwwlskqaalijopjkokkkojijl",
    "arc_hash_alg": "sha256",
}
PRINCIPAL_DECLARED = {
    "issuer": "idp.synsation.io/1234",
    "subject": "phil.b",
    "email": "phil.b@synsation.io",
    "display_name": "Declared",
}
PRINCIPAL_ACCEPTED = {
    "issuer": "idp.synsation.io/1234",
    "subject": "phil.b",
    "email": "phil.b@synsation.io",
    "display_name": "Accepted",
}
PROPS = {
    "operation": "Attach",
    "behaviour": "Attachments",
    "timestamp_declared": "2019-11-27T14:44:19Z",
    "principal_accepted": PRINCIPAL_ACCEPTED,
}
PROPS_WITH_NO_TIMESTAMP = {
    "operation": "Attach",
    "behaviour": "Attachments",
    "principal_accepted": PRINCIPAL_ACCEPTED,
}
PROPS_WITH_TIMESTAMP_ACCEPTED = {
    "operation": "Attach",
    "behaviour": "Attachments",
    "timestamp_accepted": "2021-04-08T14:44:19Z",
    "principal_accepted": PRINCIPAL_ACCEPTED,
}
PROPS_WITH_PRINCIPAL_DECLARED = {
    "operation": "Attach",
    "behaviour": "Attachments",
    "timestamp_declared": "2019-11-27T14:44:19Z",
    "principal_declared": PRINCIPAL_DECLARED,
}
PROPS_WITH_NO_PRINCIPAL = {
    "operation": "Attach",
    "behaviour": "Attachments",
    "timestamp_declared": "2019-11-27T14:44:19Z",
}

LOCATION_IDENTITY = "locations/zzzzzzzzzzzzzzzzzzzzz"
LOCATION = {
    "identity": LOCATION_IDENTITY,
    "display_name": "Somewhere",
    "description": "somewhere",
    "latitude": 0.0,
    "longitude": 0.0,
}

EVENT_ATTRS = {
    "arc_append_attachments": [
        SECONDARY_IMAGE,
        PRIMARY_IMAGE,
    ],
}
ASSET_ATTRS = {
    "external_container": "assets/xxxx",
}

IDENTITY = f"{ASSET_ID}/{EVENTS_LABEL}/xxxxxxxxxxxxxxxxxxxx"

ATTACHMENTS = {
    "arc_attachment_identity": f"{ATTACHMENTS_LABEL}/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "arc_hash_value": "jnwpjocoqsssnundwlqalsqiiqsqp;lpiwpldkndwwlskqaalijopjkokkkojijl",
    "arc_hash_alg": "sha256",
}

EVENT_ATTRS_ATTACHMENTS = {
    "operation": "Record",
    "behaviour": "RecordEvidence",
    "timestamp_declared": "2019-11-27T14:44:19Z",
    "principal_declared": PRINCIPAL_DECLARED,
    "event_attributes": {
        "arc_description": "event description",
    },
    "attachments": [
        {
            "filename": "door_open.png",
            "content_type": "image/jpg",
        },
    ],
}
REQUEST_WITH_ATTACHMENTS = {
    "operation": "Record",
    "behaviour": "RecordEvidence",
    "timestamp_declared": "2019-11-27T14:44:19Z",
    "principal_declared": PRINCIPAL_DECLARED,
    "event_attributes": {
        "arc_description": "event description",
        "arc_attachments": [
            ATTACHMENTS,
        ],
    },
}
RESPONSE_WITH_ATTACHMENTS = {
    "identity": IDENTITY,
    "operation": "Record",
    "behaviour": "RecordEvidence",
    "timestamp_declared": "2019-11-27T14:44:19Z",
    "principal_declared": PRINCIPAL_DECLARED,
    "event_attributes": {
        "arc_description": "event description",
        "arc_attachments": [
            ATTACHMENTS,
        ],
    },
}

SBOM = {
    "identity": "sboms/68e626f7-1093-4166-a0d5-5d1dd53abdf9",
    "authors": ["TestAuthorName", "TestAuthorAnotherName"],
    "supplier": "CycloneDx 1.3 XML Default Supplier",
    "component": "CycloneDx 1.3 XML Default Name",
    "version": "CycloneDx 1.3 XML Default Version",
    "hashes": [
        "SHA-1:ef969aae8d3ab29c565d579e3beeb6f4dd791ecd8996fee29fa17146332ed1ec"
    ],
    "unique_id": "urn:uuid:a24426e6-f122-4339-8b03-758a96a42e3b",
    "upload_date": "2022-03-09T09:01:20Z",
    "uploaded_by": "",
    "trusted": False,
    "lifecycle_status": "ACTIVE",
    "withdrawn_date": "",
    "published_date": "",
    "rkvst_link": "",
}

SBOM_RESULT = {
    "author": "TestAuthorName,TestAuthorAnotherName",
    "component": "CycloneDx 1.3 XML Default Name",
    "hash": "ef969aae8d3ab29c565d579e3beeb6f4dd791ecd8996fee29fa17146332ed1ec",
    "identity": "sboms/68e626f7-1093-4166-a0d5-5d1dd53abdf9",
    "repo": "",
    "supplier": "CycloneDx 1.3 XML Default Supplier",
    "uuid": "urn:uuid:a24426e6-f122-4339-8b03-758a96a42e3b",
    "version": "CycloneDx 1.3 XML Default Version",
}

EVENT_ATTRS_SBOM = {
    "operation": "Record",
    "behaviour": "RecordEvidence",
    "timestamp_declared": "2019-11-27T14:44:19Z",
    "principal_declared": PRINCIPAL_DECLARED,
    "event_attributes": {
        "arc_description": "event description",
    },
    "sbom": {
        "filename": "gen1.xml",
        "content_type": "text/xml",
        "confirm": True,
        "params": {
            "privacy": "PRIVATE",
        },
    },
}
REQUEST_WITH_SBOM = {
    "operation": "Record",
    "behaviour": "RecordEvidence",
    "timestamp_declared": "2019-11-27T14:44:19Z",
    "principal_declared": PRINCIPAL_DECLARED,
    "event_attributes": {
        "arc_description": "event description",
        "sbom_author": "TestAuthorName,TestAuthorAnotherName",
        "sbom_component": "CycloneDx 1.3 XML Default Name",
        "sbom_hash": "ef969aae8d3ab29c565d579e3beeb6f4dd791ecd8996fee29fa17146332ed1ec",
        "sbom_identity": "sboms/68e626f7-1093-4166-a0d5-5d1dd53abdf9",
        "sbom_repo": "",
        "sbom_supplier": "CycloneDx 1.3 XML Default Supplier",
        "sbom_uuid": "urn:uuid:a24426e6-f122-4339-8b03-758a96a42e3b",
        "sbom_version": "CycloneDx 1.3 XML Default Version",
    },
}
RESPONSE_WITH_SBOM = {
    "identity": IDENTITY,
    "operation": "Record",
    "behaviour": "RecordEvidence",
    "timestamp_declared": "2019-11-27T14:44:19Z",
    "principal_declared": PRINCIPAL_DECLARED,
    "event_attributes": {
        "arc_description": "event description",
        "sbom_author": "TestAuthorName,TestAuthorAnotherName",
        "sbom_component": "CycloneDx 1.3 XML Default Name",
        "sbom_hash": "ef969aae8d3ab29c565d579e3beeb6f4dd791ecd8996fee29fa17146332ed1ec",
        "sbom_identity": "sboms/68e626f7-1093-4166-a0d5-5d1dd53abdf9",
        "sbom_repo": "",
        "sbom_supplier": "CycloneDx 1.3 XML Default Supplier",
        "sbom_uuid": "urn:uuid:a24426e6-f122-4339-8b03-758a96a42e3b",
        "sbom_version": "CycloneDx 1.3 XML Default Version",
    },
}

EVENT_ATTRS_SBOMATTACHMENT = {
    "operation": "Record",
    "behaviour": "RecordEvidence",
    "timestamp_declared": "2019-11-27T14:44:19Z",
    "principal_declared": PRINCIPAL_DECLARED,
    "event_attributes": {
        "arc_description": "event description",
    },
    "attachments": [
        {
            "filename": "gen1.xml",
            "content_type": "text/xml",
            "type": SBOM_RELEASE,
        },
    ],
}
REQUEST_WITH_SBOMATTACHMENT = {
    "operation": "Record",
    "behaviour": "RecordEvidence",
    "timestamp_declared": "2019-11-27T14:44:19Z",
    "principal_declared": PRINCIPAL_DECLARED,
    "event_attributes": {
        "arc_description": "event description",
        "sbom_author": "TestAuthorName,TestAuthorAnotherName",
        "sbom_component": "CycloneDx 1.3 XML Default Name",
        "sbom_hash": "ef969aae8d3ab29c565d579e3beeb6f4dd791ecd8996fee29fa17146332ed1ec",
        "sbom_identity": f"{ATTACHMENTS_LABEL}/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
        "sbom_repo": "",
        "sbom_supplier": "CycloneDx 1.3 XML Default Supplier",
        "sbom_uuid": "urn:uuid:a24426e6-f122-4339-8b03-758a96a42e3b",
        "sbom_version": "CycloneDx 1.3 XML Default Version",
        "arc_attachments": [
            ATTACHMENTS,
        ],
    },
}
RESPONSE_WITH_SBOMATTACHMENT = {
    "identity": IDENTITY,
    "operation": "Record",
    "behaviour": "RecordEvidence",
    "timestamp_declared": "2019-11-27T14:44:19Z",
    "principal_declared": PRINCIPAL_DECLARED,
    "event_attributes": {
        "arc_description": "event description",
        "sbom_author": "TestAuthorName,TestAuthorAnotherName",
        "sbom_component": "CycloneDx 1.3 XML Default Name",
        "sbom_hash": "ef969aae8d3ab29c565d579e3beeb6f4dd791ecd8996fee29fa17146332ed1ec",
        "sbom_identity": f"{ATTACHMENTS_LABEL}/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
        "sbom_repo": "",
        "sbom_supplier": "CycloneDx 1.3 XML Default Supplier",
        "sbom_uuid": "urn:uuid:a24426e6-f122-4339-8b03-758a96a42e3b",
        "sbom_version": "CycloneDx 1.3 XML Default Version",
        "arc_attachments": [
            ATTACHMENTS,
        ],
    },
}

EVENT_ATTRS_LOCATION = {
    "operation": "Record",
    "behaviour": "RecordEvidence",
    "timestamp_declared": "2019-11-27T14:44:19Z",
    "principal_declared": PRINCIPAL_DECLARED,
    "event_attributes": {
        "arc_description": "event description",
    },
    "location": {
        "selector": [
            "display_name",
        ],
        "display_name": "Somewhere",
        "description": "somewhere",
        "latitude": 0.0,
        "longitude": 0.0,
    },
}
REQUEST_WITH_LOCATION = {
    "operation": "Record",
    "behaviour": "RecordEvidence",
    "timestamp_declared": "2019-11-27T14:44:19Z",
    "principal_declared": PRINCIPAL_DECLARED,
    "event_attributes": {
        "arc_description": "event description",
        "arc_location_identity": LOCATION_IDENTITY,
    },
}
RESPONSE_WITH_LOCATION = {
    "identity": IDENTITY,
    "operation": "Record",
    "behaviour": "RecordEvidence",
    "timestamp_declared": "2019-11-27T14:44:19Z",
    "principal_declared": PRINCIPAL_DECLARED,
    "event_attributes": {
        "arc_description": "event description",
        "arc_location_identity": LOCATION_IDENTITY,
    },
}
REQUEST = {
    **PROPS,
    "event_attributes": EVENT_ATTRS,
}

REQUEST_WITH_ASSET_ATTRS = {
    **REQUEST,
    "asset_attributes": ASSET_ATTRS,
}

RESPONSE = {
    **PROPS,
    "identity": IDENTITY,
    "event_attributes": EVENT_ATTRS,
    "confirmation_status": "CONFIRMED",
}
RESPONSE_WITH_ASSET_ATTRS = {
    **RESPONSE,
    "asset_attributes": ASSET_ATTRS,
}
RESPONSE_NO_CONFIRMATION = {
    **PROPS,
    "identity": IDENTITY,
    "event_attributes": EVENT_ATTRS,
}
RESPONSE_PENDING = {
    **PROPS,
    "identity": IDENTITY,
    "event_attributes": EVENT_ATTRS,
    "confirmation_status": "PENDING",
}
RESPONSE_FAILED = {
    **PROPS,
    "identity": IDENTITY,
    "event_attributes": EVENT_ATTRS,
    "confirmation_status": "FAILED",
}
RESPONSE_WITH_NO_TIMESTAMP = {
    **PROPS_WITH_NO_TIMESTAMP,
    "identity": IDENTITY,
    "event_attributes": EVENT_ATTRS,
    "confirmation_status": "CONFIRMED",
}
RESPONSE_WITH_TIMESTAMP_ACCEPTED = {
    **PROPS_WITH_TIMESTAMP_ACCEPTED,
    "identity": IDENTITY,
    "event_attributes": EVENT_ATTRS,
    "confirmation_status": "CONFIRMED",
}

RESPONSE_WITH_PRINCIPAL_DECLARED = {
    **PROPS_WITH_PRINCIPAL_DECLARED,
    "identity": IDENTITY,
    "event_attributes": EVENT_ATTRS,
    "confirmation_status": "CONFIRMED",
}

RESPONSE_WITH_NO_PRINCIPAL = {
    **PROPS_WITH_NO_PRINCIPAL,
    "identity": IDENTITY,
    "event_attributes": EVENT_ATTRS,
    "confirmation_status": "CONFIRMED",
}


class TestEvent(TestCase):
    """
    Test Archivist Events Create method
    """

    maxDiff = None

    def test_event_who_accepted(self):
        event = Event(**RESPONSE)
        self.assertEqual(
            event.who,
            "Accepted",
            msg="Incorrect who",
        )

    def test_event_who_none(self):
        event = Event(**RESPONSE_WITH_NO_PRINCIPAL)
        self.assertEqual(
            event.who,
            None,
            msg="who should be None",
        )

    def test_event_who_declared(self):
        event = Event(**RESPONSE_WITH_PRINCIPAL_DECLARED)
        self.assertEqual(
            event.who,
            "Declared",
            msg="Incorrect who",
        )

    def test_event_when_declared(self):
        event = Event(**RESPONSE)
        self.assertEqual(
            event.when,
            "2019-11-27T14:44:19Z",
            msg="Incorrect when",
        )

    def test_event_when_accepted(self):
        event = Event(**RESPONSE_WITH_TIMESTAMP_ACCEPTED)
        self.assertEqual(
            event.when,
            "2021-04-08T14:44:19Z",
            msg="Incorrect when",
        )

    def test_event_when_none(self):
        event = Event(**RESPONSE_WITH_NO_TIMESTAMP)
        self.assertEqual(
            event.when,
            None,
            msg="Incorrect when",
        )


class TestEvents(TestCase):
    """
    Test Archivist Events Create method
    """

    maxDiff = None

    def setUp(self):
        self.arch = Archivist("url", "authauthauth", max_time=1)

    def tearDown(self):
        self.arch = None

    def test_events_str(self):
        """
        Test events str
        """
        self.assertEqual(
            str(self.arch.events),
            "EventsClient(url)",
            msg="Incorrect str",
        )

    def test_events_create(self):
        """
        Test event creation
        """
        with mock.patch.object(self.arch._session, "post") as mock_post:
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
            self.arch._session, "post"
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

    def test_events_create_with_upload_sbom(self):
        """
        Test event creation
        """
        with mock.patch.object(
            self.arch._session, "post"
        ) as mock_post, mock.patch.object(
            self.arch.sboms, "create"
        ) as mock_sboms_create:
            mock_post.return_value = MockResponse(200, **RESPONSE_WITH_SBOM)
            mock_sboms_create.return_value = SBOM_RESULT

            event = self.arch.events.create_from_data(
                ASSET_ID, EVENT_ATTRS_SBOM, confirm=False
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
                    "json": REQUEST_WITH_SBOM,
                    "headers": {
                        "authorization": "Bearer authauthauth",
                    },
                    "verify": True,
                },
                msg="CREATE method kwargs called incorrectly",
            )
            self.assertEqual(
                event,
                RESPONSE_WITH_SBOM,
                msg="CREATE method called incorrectly",
            )

    def test_events_create_with_upload_sbom_as_attachment(self):
        """
        Test event creation
        """
        with mock.patch.object(
            self.arch._session, "post"
        ) as mock_post, mock.patch.object(
            self.arch.attachments, "create"
        ) as mock_attachments_create, mock.patch.object(
            self.arch.sboms, "parse"
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
            self.arch._session, "post"
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

    def test_events_create_with_asset_attrs(self):
        """
        Test event creation
        """
        with mock.patch.object(self.arch._session, "post") as mock_post:
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

    def test_events_create_with_confirmation(self):
        """
        Test event creation
        """
        with mock.patch.object(
            self.arch._session, "post"
        ) as mock_post, mock.patch.object(self.arch._session, "get") as mock_get:

            mock_post.return_value = MockResponse(200, **RESPONSE)
            mock_get.return_value = MockResponse(200, **RESPONSE)

            event = self.arch.events.create(ASSET_ID, PROPS, EVENT_ATTRS, confirm=True)
            self.assertEqual(
                event,
                RESPONSE,
                msg="CREATE method called incorrectly",
            )

    def test_events_create_with_explicit_confirmation(self):
        """
        Test event creation
        """
        with mock.patch.object(
            self.arch._session, "post"
        ) as mock_post, mock.patch.object(self.arch._session, "get") as mock_get:

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
            self.arch._session, "post"
        ) as mock_post, mock.patch.object(self.arch._session, "get") as mock_get:
            mock_post.return_value = MockResponse(200, **RESPONSE)
            mock_get.return_value = MockResponse(200, **RESPONSE_NO_CONFIRMATION)

            with self.assertRaises(ArchivistUnconfirmedError):
                event = self.arch.events.create(
                    ASSET_ID, PROPS, EVENT_ATTRS, confirm=True
                )

    def test_events_create_with_confirmation_pending_status(self):
        """
        Test asset confirmation
        """
        with mock.patch.object(
            self.arch._session, "post"
        ) as mock_post, mock.patch.object(self.arch._session, "get") as mock_get:
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

    def test_events_create_with_confirmation_failed_status(self):
        """
        Test asset confirmation
        """
        with mock.patch.object(
            self.arch._session, "post"
        ) as mock_post, mock.patch.object(self.arch._session, "get") as mock_get:
            mock_post.return_value = MockResponse(200, **RESPONSE)
            mock_get.side_effect = [
                MockResponse(200, **RESPONSE_PENDING),
                MockResponse(200, **RESPONSE_FAILED),
            ]
            with self.assertRaises(ArchivistUnconfirmedError):
                event = self.arch.events.create(
                    ASSET_ID, PROPS, EVENT_ATTRS, confirm=True
                )

    def test_events_create_with_confirmation_always_pending_status(self):
        """
        Test asset confirmation
        """
        with mock.patch.object(
            self.arch._session, "post"
        ) as mock_post, mock.patch.object(self.arch._session, "get") as mock_get:
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
                event = self.arch.events.create(
                    ASSET_ID, PROPS, EVENT_ATTRS, confirm=True
                )

    def test_events_read(self):
        """
        Test event counting
        """
        with mock.patch.object(self.arch._session, "get") as mock_get:
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
                        "verify": True,
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
        Test event counting
        """
        with mock.patch.object(self.arch._session, "get") as mock_get:
            mock_get.return_value = MockResponse(200, **RESPONSE)

            event = self.arch.events.read(IDENTITY)
            self.assertEqual(
                event,
                RESPONSE,
                msg="GET method called incorrectly",
            )

    def test_events_count(self):
        """
        Test event counting
        """
        with mock.patch.object(self.arch._session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                headers={HEADERS_TOTAL_COUNT: 1},
                events=[
                    RESPONSE,
                ],
            )

            count = self.arch.events.count(asset_id=ASSET_ID)
            self.assertEqual(
                count,
                1,
                msg="Incorrect count",
            )
            self.assertEqual(
                tuple(mock_get.call_args),
                (
                    (
                        (
                            f"url/{ROOT}/{ASSETS_SUBPATH}"
                            f"/{ASSETS_LABEL}/xxxxxxxxxxxxxxxxxxxx"
                            f"/{EVENTS_LABEL}"
                        ),
                    ),
                    {
                        "headers": {
                            "authorization": "Bearer authauthauth",
                            HEADERS_REQUEST_TOTAL_COUNT: "true",
                        },
                        "params": {"page_size": 1},
                        "verify": True,
                    },
                ),
                msg="GET method called incorrectly",
            )

    def test_events_count_with_props_params(self):
        """
        Test event counting
        """
        with mock.patch.object(self.arch._session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                headers={HEADERS_TOTAL_COUNT: 1},
                events=[
                    RESPONSE,
                ],
            )

            count = self.arch.events.count(
                asset_id=ASSET_ID,
                props={
                    "confirmation_status": "CONFIRMED",
                },
            )
            self.assertEqual(
                tuple(mock_get.call_args),
                (
                    (
                        (
                            f"url/{ROOT}/{ASSETS_SUBPATH}"
                            f"/{ASSETS_LABEL}/xxxxxxxxxxxxxxxxxxxx"
                            f"/{EVENTS_LABEL}"
                        ),
                    ),
                    {
                        "headers": {
                            "authorization": "Bearer authauthauth",
                            HEADERS_REQUEST_TOTAL_COUNT: "true",
                        },
                        "params": {"page_size": 1, "confirmation_status": "CONFIRMED"},
                        "verify": True,
                    },
                ),
                msg="GET method called incorrectly",
            )

    def test_events_count_with_attrs_params(self):
        """
        Test event counting
        """
        with mock.patch.object(self.arch._session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                headers={HEADERS_TOTAL_COUNT: 1},
                events=[
                    RESPONSE,
                ],
            )

            count = self.arch.events.count(
                asset_id=ASSET_ID,
                attrs={"arc_firmware_version": "1.0"},
            )
            self.assertEqual(
                tuple(mock_get.call_args),
                (
                    (
                        (
                            f"url/{ROOT}/{ASSETS_SUBPATH}"
                            f"/{ASSETS_LABEL}/xxxxxxxxxxxxxxxxxxxx"
                            f"/{EVENTS_LABEL}"
                        ),
                    ),
                    {
                        "headers": {
                            "authorization": "Bearer authauthauth",
                            HEADERS_REQUEST_TOTAL_COUNT: "true",
                        },
                        "params": {
                            "page_size": 1,
                            "event_attributes.arc_firmware_version": "1.0",
                        },
                        "verify": True,
                    },
                ),
                msg="GET method called incorrectly",
            )

    def test_events_count_with_wildcard_asset(self):
        """
        Test event counting
        """
        with mock.patch.object(self.arch._session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                headers={HEADERS_TOTAL_COUNT: 1},
                events=[
                    RESPONSE,
                ],
            )

            count = self.arch.events.count(
                attrs={"arc_firmware_version": "1.0"},
            )
            self.assertEqual(
                tuple(mock_get.call_args),
                (
                    (
                        (
                            f"url/{ROOT}/{ASSETS_SUBPATH}"
                            f"/{ASSETS_WILDCARD}"
                            f"/{EVENTS_LABEL}"
                        ),
                    ),
                    {
                        "headers": {
                            "authorization": "Bearer authauthauth",
                            HEADERS_REQUEST_TOTAL_COUNT: "true",
                        },
                        "params": {
                            "page_size": 1,
                            "event_attributes.arc_firmware_version": "1.0",
                        },
                        "verify": True,
                    },
                ),
                msg="GET method called incorrectly",
            )

    def test_events_wait_for_confirmed(self):
        """
        Test event counting
        """
        ## last call to get looks for FAILED assets
        status = (
            {"page_size": 1},
            {"page_size": 1, "confirmation_status": "PENDING"},
            {"page_size": 1, "confirmation_status": "FAILED"},
        )
        with mock.patch.object(self.arch._session, "get") as mock_get:
            mock_get.side_effect = [
                MockResponse(
                    200,
                    headers={HEADERS_TOTAL_COUNT: 2},
                    assets=[
                        RESPONSE_PENDING,
                    ],
                ),
                MockResponse(
                    200,
                    headers={HEADERS_TOTAL_COUNT: 0},
                    assets=[],
                ),
                MockResponse(
                    200,
                    headers={HEADERS_TOTAL_COUNT: 0},
                    assets=[],
                ),
            ]

            self.arch.events.wait_for_confirmed()
            for i, a in enumerate(mock_get.call_args_list):
                self.assertEqual(
                    tuple(a),
                    (
                        (
                            (
                                f"url/{ROOT}/{ASSETS_SUBPATH}"
                                f"/{ASSETS_WILDCARD}"
                                f"/{EVENTS_LABEL}"
                            ),
                        ),
                        {
                            "headers": {
                                "authorization": "Bearer authauthauth",
                                HEADERS_REQUEST_TOTAL_COUNT: "true",
                            },
                            "params": status[i],
                            "verify": True,
                        },
                    ),
                    msg="GET method called incorrectly",
                )

    def test_events_wait_for_confirmed_not_found(self):
        """
        Test event counting
        """
        with mock.patch.object(self.arch._session, "get") as mock_get:
            mock_get.side_effect = [
                MockResponse(
                    200,
                    headers={HEADERS_TOTAL_COUNT: 0},
                    assets=[
                        RESPONSE_PENDING,
                    ],
                ),
            ]

            with self.assertRaises(ArchivistNotFoundError):
                self.arch.events.wait_for_confirmed()

    def test_events_list(self):
        """
        Test event listing
        """
        with mock.patch.object(self.arch._session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                events=[
                    RESPONSE,
                ],
            )

            events = list(self.arch.events.list(asset_id=ASSET_ID))
            self.assertEqual(
                len(events),
                1,
                msg="incorrect number of events",
            )
            for event in events:
                self.assertEqual(
                    event,
                    RESPONSE,
                    msg="Incorrect event listed",
                )

            for a in mock_get.call_args_list:
                self.assertEqual(
                    tuple(a),
                    (
                        (
                            (
                                f"url/{ROOT}/{ASSETS_SUBPATH}"
                                f"/{ASSETS_LABEL}/xxxxxxxxxxxxxxxxxxxx"
                                f"/{EVENTS_LABEL}"
                            ),
                        ),
                        {
                            "headers": {
                                "authorization": "Bearer authauthauth",
                            },
                            "params": {},
                            "verify": True,
                        },
                    ),
                    msg="GET method called incorrectly",
                )

    def test_events_list_with_params(self):
        """
        Test event listing
        """
        with mock.patch.object(self.arch._session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                events=[
                    RESPONSE,
                ],
            )

            events = list(
                self.arch.events.list(
                    asset_id=ASSET_ID,
                    props={
                        "confirmation_status": "CONFIRMED",
                    },
                    attrs={"arc_firmware_version": "1.0"},
                )
            )
            self.assertEqual(
                len(events),
                1,
                msg="incorrect number of events",
            )
            for event in events:
                self.assertEqual(
                    event,
                    RESPONSE,
                    msg="Incorrect event listed",
                )

            for a in mock_get.call_args_list:
                self.assertEqual(
                    tuple(a),
                    (
                        (
                            (
                                f"url/{ROOT}/{ASSETS_SUBPATH}"
                                f"/{ASSETS_LABEL}/xxxxxxxxxxxxxxxxxxxx"
                                f"/{EVENTS_LABEL}"
                            ),
                        ),
                        {
                            "headers": {
                                "authorization": "Bearer authauthauth",
                            },
                            "params": {
                                "confirmation_status": "CONFIRMED",
                                "event_attributes.arc_firmware_version": "1.0",
                            },
                            "verify": True,
                        },
                    ),
                    msg="GET method called incorrectly",
                )

    def test_events_list_with_wildcard_asset(self):
        """
        Test event listing
        """
        with mock.patch.object(self.arch._session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                events=[
                    RESPONSE,
                ],
            )

            events = list(
                self.arch.events.list(
                    props={
                        "confirmation_status": "CONFIRMED",
                    },
                    attrs={"arc_firmware_version": "1.0"},
                )
            )
            self.assertEqual(
                len(events),
                1,
                msg="incorrect number of events",
            )
            for event in events:
                self.assertEqual(
                    event,
                    RESPONSE,
                    msg="Incorrect event listed",
                )

            for a in mock_get.call_args_list:
                self.assertEqual(
                    tuple(a),
                    (
                        (
                            (
                                f"url/{ROOT}/{ASSETS_SUBPATH}"
                                f"/{ASSETS_WILDCARD}"
                                f"/{EVENTS_LABEL}"
                            ),
                        ),
                        {
                            "headers": {
                                "authorization": "Bearer authauthauth",
                            },
                            "params": {
                                "confirmation_status": "CONFIRMED",
                                "event_attributes.arc_firmware_version": "1.0",
                            },
                            "verify": True,
                        },
                    ),
                    msg="GET method called incorrectly",
                )

    def test_events_read_by_signature(self):
        """
        Test event listing
        """
        with mock.patch.object(self.arch._session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                events=[
                    RESPONSE,
                ],
            )

            event = self.arch.events.read_by_signature(asset_id=ASSET_ID)
            self.assertEqual(
                event,
                RESPONSE,
                msg="Incorrect event listed",
            )

            self.assertEqual(
                tuple(mock_get.call_args),
                (
                    (
                        (
                            f"url/{ROOT}/{ASSETS_SUBPATH}"
                            f"/{ASSETS_LABEL}/xxxxxxxxxxxxxxxxxxxx"
                            f"/{EVENTS_LABEL}"
                        ),
                    ),
                    {
                        "headers": {
                            "authorization": "Bearer authauthauth",
                        },
                        "params": {"page_size": 2},
                        "verify": True,
                    },
                ),
                msg="GET method called incorrectly",
            )
