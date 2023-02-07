"""
Test events constants
"""

from unittest import TestCase

from archivist.archivist import Archivist
from archivist.constants import (
    ASSETS_LABEL,
    ATTACHMENTS_LABEL,
    EVENTS_LABEL,
    SBOM_RELEASE,
)

# pylint: disable=missing-docstring
# pylint: disable=protected-access
# pylint: disable=unused-variable
# pylint: disable=too-many-public-methods

ASSET_ID = f"{ASSETS_LABEL}/xxxxxxxxxxxxxxxxxxxx"

PRIMARY_IMAGE = {
    "arc_blob_identity": f"{ATTACHMENTS_LABEL}/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "arc_display_name": "an attachment 2",
    "arc_blob_hash_value": "042aea10a0f14f2d391373599be69d53a75dde9951fc3d3cd10b6100aa7a9f24",
    "arc_blob_hash_alg": "sha256",
}
SECONDARY_IMAGE = {
    "arc_blob_identity": f"{ATTACHMENTS_LABEL}/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "arc_display_name": "an attachment 1",
    "arc_blob_hash_value": "jnwpjocoqsssnundwlqalsqiiqsqp;lpiwpldkndwwlskqaalijopjkokkkojijl",
    "arc_blob_hash_alg": "sha256",
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
    "arc_attribute_type": "arc_attachment",
    "arc_blob_identity": f"{ATTACHMENTS_LABEL}/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "arc_blob_hash_value": "jnwpjocoqsssnundwlqalsqiiqsqp;lpiwpldkndwwlskqaalijopjkokkkojijl",
    "arc_blob_hash_alg": "sha256",
    "arc_file_name": "",
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
            "attachment": "door open",
            "filename": "door_open.png",
            "content_type": "image/jpg",
        },
        {
            "filename": "door_closed.png",
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
        "door open": ATTACHMENTS,
        "door_closed_png": ATTACHMENTS,
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
        "door open": ATTACHMENTS,
        "door_closed_png": ATTACHMENTS,
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
            "attachment": "sbom_document",
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
        "sbom_document": ATTACHMENTS,
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
        "sbom_document": ATTACHMENTS,
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
EVENT_ATTRS_LOCATION_IDENTITY = {
    "operation": "Record",
    "behaviour": "RecordEvidence",
    "timestamp_declared": "2019-11-27T14:44:19Z",
    "principal_declared": PRINCIPAL_DECLARED,
    "event_attributes": {
        "arc_description": "event description",
    },
    "location": {
        "identity": LOCATION_IDENTITY,
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


PUBLICURL = (
    "https://app.rkvst.io/archivist/publicassets/13f23360-14c7-4d00-ac29-0a862584060e/"
    f"{EVENTS_LABEL}/xxxxxxxxxxxxxxxxxxxx"
)
RESPONSE_PUBLICURL = {
    "publicurl": PUBLICURL,
}
RESPONSE_BAD_PUBLICURL = {
    "badpublicurl": PUBLICURL,
}


class TestEventsBase(TestCase):
    """
    Test Archivist Events Create method
    """

    maxDiff = None

    def setUp(self):
        self.arch = Archivist("url", "authauthauth", max_time=1)

    def tearDown(self):
        self.arch.close()
