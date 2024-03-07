"""
Test assets constants
"""

from unittest import TestCase

from archivist.archivist import Archivist
from archivist.constants import (
    ASSET_BEHAVIOURS,
    ASSETS_LABEL,
    ASSETS_SUBPATH,
    ATTACHMENTS_LABEL,
    LOCATIONS_LABEL,
)
from archivist.proof_mechanism import ProofMechanism

# pylint: disable=missing-docstring
# pylint: disable=protected-access
# pylint: disable=unused-variable

PRIMARY_IMAGE = {
    "arc_attribute_type": "arc_attachment",
    "arc_display_name": "arc_primary_image",
    "arc_blob_identity": "blobs/87b1a84c-1c6f-442b-923e-a97516f4d275",
    "arc_blob_hash_alg": "SHA256",
    "arc_blob_hash_value": "246c316e2cd6971ce5c83a3e61f9880fa6e2f14ae2976ee03500eb282fd03a60",
}
SECONDARY_IMAGE = {
    "arc_attribute_type": "arc_attachment",
    "arc_display_name": "arc_secondary_image",
    "arc_blob_identity": "blobs/87b1a84c-1c6f-442b-923e-a97516f4d275",
    "arc_blob_hash_alg": "SHA256",
    "arc_blob_hash_value": "246c316e2cd6971ce5c83a3e61f9880fa6e2f14ae2976ee03500eb282fd03a60",
}
TERTIARY_IMAGE = {
    "arc_attribute_type": "arc_attachment",
    "arc_blob_identity": "blobs/87b1a84c-1c6f-442b-923e-a97516f4d275",
    "arc_blob_hash_alg": "SHA256",
    "arc_blob_hash_value": "246c316e2cd6971ce5c83a3e61f9880fa6e2f14ae2976ee03500eb282fd03a60",
}
ASSET_NAME = "tcl.ppj.003"
# also has no arc_display_name
ATTRS_NO_ATTACHMENTS = {
    "arc_firmware_version": "1.0",
    "arc_serial_number": "vtl-x4-07",
    "arc_description": "Traffic flow control light at A603 North East",
    "arc_display_type": "Traffic light with violation camera",
    "some_custom_attribute": "value",
}

IDENTITY = f"{ASSETS_LABEL}/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
SUBPATH = f"{ASSETS_SUBPATH}/{ASSETS_LABEL}"

FIXTURES_ATTRIBUTES = {
    "arc_namespace": "namespace",
}
FIXTURES = {
    "assets": {
        "attributes": {
            "arc_namespace": "namespace",
        },
    },
}
ATTRS_FIXTURES = {
    "arc_namespace": "namespace",
    "arc_firmware_version": "1.0",
    "arc_serial_number": "vtl-x4-07",
    "arc_description": "Traffic flow control light at A603 North East",
    "arc_display_type": "Traffic light with violation camera",
    "some_custom_attribute": "value",
    "arc_display_name": ASSET_NAME,
    "arc_attachments": [
        TERTIARY_IMAGE,
        SECONDARY_IMAGE,
        PRIMARY_IMAGE,
    ],
}

# case 1 create
SIMPLE_HASH = {
    "proof_mechanism": ProofMechanism.SIMPLE_HASH.name,
}
MERKLE_LOG = {
    "proof_mechanism": ProofMechanism.MERKLE_LOG.name,
}
ATTRS = {
    "arc_firmware_version": "1.0",
    "arc_serial_number": "vtl-x4-07",
    "arc_description": "Traffic flow control light at A603 North East",
    "arc_display_type": "Traffic light with violation camera",
    "some_custom_attribute": "value",
    "arc_display_name": ASSET_NAME,
    "arc_attachments": [
        TERTIARY_IMAGE,
        SECONDARY_IMAGE,
        PRIMARY_IMAGE,
    ],
}
REQUEST_SIMPLE_HASH = {
    "behaviours": ASSET_BEHAVIOURS,
    "proof_mechanism": ProofMechanism.SIMPLE_HASH.name,
    "attributes": {
        "arc_firmware_version": "1.0",
        "arc_serial_number": "vtl-x4-07",
        "arc_description": "Traffic flow control light at A603 North East",
        "arc_display_type": "Traffic light with violation camera",
        "some_custom_attribute": "value",
        "arc_display_name": ASSET_NAME,
        "arc_attachments": [
            TERTIARY_IMAGE,
            SECONDARY_IMAGE,
            PRIMARY_IMAGE,
        ],
    },
}
REQUEST_KWARGS_MERKLE_LOG = {
    "json": {
        "behaviours": ASSET_BEHAVIOURS,
        "proof_mechanism": ProofMechanism.MERKLE_LOG.name,
        "attributes": {
            "arc_firmware_version": "1.0",
            "arc_serial_number": "vtl-x4-07",
            "arc_description": "Traffic flow control light at A603 North East",
            "arc_display_type": "Traffic light with violation camera",
            "some_custom_attribute": "value",
            "arc_display_name": ASSET_NAME,
            "arc_attachments": [
                TERTIARY_IMAGE,
                SECONDARY_IMAGE,
                PRIMARY_IMAGE,
            ],
        },
    },
    "headers": {
        "authorization": "Bearer authauthauth",
    },
    "verify": True,
}
REQUEST_KWARGS_SIMPLE_HASH = {
    "json": {
        "behaviours": ASSET_BEHAVIOURS,
        "proof_mechanism": ProofMechanism.SIMPLE_HASH.name,
        "attributes": {
            "arc_firmware_version": "1.0",
            "arc_serial_number": "vtl-x4-07",
            "arc_description": "Traffic flow control light at A603 North East",
            "arc_display_type": "Traffic light with violation camera",
            "some_custom_attribute": "value",
            "arc_display_name": ASSET_NAME,
            "arc_attachments": [
                TERTIARY_IMAGE,
                SECONDARY_IMAGE,
                PRIMARY_IMAGE,
            ],
        },
    },
    "headers": {
        "authorization": "Bearer authauthauth",
    },
    "verify": True,
}
RESPONSE = {
    "identity": IDENTITY,
    "behaviours": ASSET_BEHAVIOURS,
    "attributes": {
        "arc_firmware_version": "1.0",
        "arc_serial_number": "vtl-x4-07",
        "arc_description": "Traffic flow control light at A603 North East",
        "arc_display_type": "Traffic light with violation camera",
        "some_custom_attribute": "value",
        "arc_display_name": ASSET_NAME,
        "arc_attachments": [
            TERTIARY_IMAGE,
            SECONDARY_IMAGE,
            PRIMARY_IMAGE,
        ],
    },
    "confirmation_status": "CONFIRMED",
}

# case 2 create if not exists
REQUEST_EXISTS_SIMPLE_HASH = {
    "selector": [
        {
            "attributes": [
                "arc_display_name",
                "arc_namespace",
            ]
        },
    ],
    "behaviours": ASSET_BEHAVIOURS,
    "proof_mechanism": ProofMechanism.SIMPLE_HASH.name,
    "attributes": {
        "arc_display_name": ASSET_NAME,
        "arc_namespace": "namespace",
        "arc_firmware_version": "1.0",
        "arc_serial_number": "vtl-x4-07",
        "arc_description": "Traffic flow control light at A603 North East",
        "arc_display_type": "Traffic light with violation camera",
        "some_custom_attribute": "value",
    },
}
REQUEST_EXISTS_KWARGS_SIMPLE_HASH = {
    "json": {
        "behaviours": ASSET_BEHAVIOURS,
        "proof_mechanism": ProofMechanism.SIMPLE_HASH.name,
        "attributes": {
            "arc_display_name": ASSET_NAME,
            "arc_namespace": "namespace",
            "arc_firmware_version": "1.0",
            "arc_serial_number": "vtl-x4-07",
            "arc_description": "Traffic flow control light at A603 North East",
            "arc_display_type": "Traffic light with violation camera",
            "some_custom_attribute": "value",
        },
    },
    "headers": {
        "authorization": "Bearer authauthauth",
    },
    "verify": True,
}
RESPONSE_EXISTS = {
    "identity": IDENTITY,
    "behaviours": ASSET_BEHAVIOURS,
    "attributes": {
        "arc_display_name": ASSET_NAME,
        "arc_namespace": "namespace",
        "arc_firmware_version": "1.0",
        "arc_serial_number": "vtl-x4-07",
        "arc_description": "Traffic flow control light at A603 North East",
        "arc_display_type": "Traffic light with violation camera",
        "some_custom_attribute": "value",
    },
    "confirmation_status": "CONFIRMED",
    "tracked": "TRACKED",
}

# case 3 create if not exists with attachments
REQUEST_EXISTS_ATTACHMENTS_SIMPLE_HASH = {
    "selector": [
        {
            "attributes": [
                "arc_display_name",
                "arc_namespace",
            ]
        },
    ],
    "behaviours": ASSET_BEHAVIOURS,
    "proof_mechanism": ProofMechanism.SIMPLE_HASH.name,
    "attributes": {
        "arc_display_name": ASSET_NAME,
        "arc_namespace": "namespace",
        "arc_firmware_version": "1.0",
        "arc_serial_number": "vtl-x4-07",
        "arc_description": "Traffic flow control light at A603 North East",
        "arc_display_type": "Traffic light with violation camera",
        "some_custom_attribute": "value",
    },
    "attachments": [
        {
            "filename": "test_filename1",
            "content_type": "image/jpg",
        },
        {
            "attachment": "test_filename2",
            "filename": "test_filename1",
            "content_type": "image/jpg",
        },
    ],
}
REQUEST_EXISTS_KWARGS_ATTACHMENTS_SIMPLE_HASH = {
    "json": {
        "behaviours": ASSET_BEHAVIOURS,
        "proof_mechanism": ProofMechanism.SIMPLE_HASH.name,
        "attributes": {
            "arc_display_name": ASSET_NAME,
            "arc_namespace": "namespace",
            "arc_firmware_version": "1.0",
            "arc_serial_number": "vtl-x4-07",
            "arc_description": "Traffic flow control light at A603 North East",
            "arc_display_type": "Traffic light with violation camera",
            "some_custom_attribute": "value",
            "test_filename1": {
                "arc_attribute_type": "arc_attachment",
                "arc_blob_identity": f"{ATTACHMENTS_LABEL}/xxxxxxxx",
                "arc_display_name": "arc_primary_image",
                "arc_blob_hash_alg": "SHA256",
                "arc_blob_hash_value": (
                    "246c316e2cd6971ce5c83a3e61f9"
                    "880fa6e2f14ae2976ee03500eb282fd03a60"
                ),
            },
            "test_filename2": {
                "arc_attribute_type": "arc_attachment",
                "arc_blob_identity": f"{ATTACHMENTS_LABEL}/xxxxxxxx",
                "arc_display_name": "arc_primary_image",
                "arc_blob_hash_alg": "SHA256",
                "arc_blob_hash_value": (
                    "246c316e2cd6971ce5c83a3e61f9"
                    "880fa6e2f14ae2976ee03500eb282fd03a60"
                ),
            },
        },
    },
    "headers": {
        "authorization": "Bearer authauthauth",
    },
    "verify": True,
}
RESPONSE_ATTACHMENTS = {
    "arc_attribute_type": "arc_attachment",
    "arc_blob_identity": f"{ATTACHMENTS_LABEL}/xxxxxxxx",
    "arc_display_name": "arc_primary_image",
    "arc_blob_hash_alg": "SHA256",
    "arc_blob_hash_value": "246c316e2cd6971ce5c83a3e61f9880fa6e2f14ae2976ee03500eb282fd03a60",
}
RESPONSE_EXISTS_ATTACHMENTS = {
    "identity": IDENTITY,
    "behaviours": ASSET_BEHAVIOURS,
    "attributes": {
        "arc_namespace": "namespace",
        "arc_firmware_version": "1.0",
        "arc_serial_number": "vtl-x4-07",
        "arc_description": "Traffic flow control light at A603 North East",
        "arc_display_type": "Traffic light with violation camera",
        "some_custom_attribute": "value",
        "arc_display_name": ASSET_NAME,
        "test_filename1": [
            {
                "arc_attribute_type": "arc_attachment",
                "arc_blob_identity": "blobs/87b1a84c-1c6f-442b-923e-a97516f4d275",
                "arc_display_name": "arc_primary_image",
                "arc_blob_hash_alg": "SHA256",
                "arc_blob_hash_value": (
                    "246c316e2cd6971ce5c83a3e61f988"
                    "0fa6e2f14ae2976ee03500eb282fd03a60"
                ),
            },
        ],
    },
    "confirmation_status": "CONFIRMED",
    "tracked": "TRACKED",
}

# case 4 create if not exists with location
REQUEST_EXISTS_LOCATION_SIMPLE_HASH = {
    "selector": [
        {
            "attributes": [
                "arc_display_name",
                "arc_namespace",
            ]
        },
    ],
    "behaviours": ASSET_BEHAVIOURS,
    "proof_mechanism": ProofMechanism.SIMPLE_HASH.name,
    "attributes": {
        "arc_display_name": ASSET_NAME,
        "arc_namespace": "namespace",
        "arc_firmware_version": "1.0",
        "arc_serial_number": "vtl-x4-07",
        "arc_description": "Traffic flow control light at A603 North East",
        "arc_display_type": "Traffic light with violation camera",
        "some_custom_attribute": "value",
    },
    "location": {
        "selector": [
            "display_name",
            {
                "attributes": [
                    "director",
                ]
            },
        ],
        "display_name": "Macclesfield, Cheshire",
        "description": "Manufacturing site, North West England, Macclesfield, Cheshire",
        "latitude": "53.2546799",
        "longitude": "-2.1213956,14.54",
        "attributes": {
            "director": "John Smith",
            "address": "Bridgewater, Somerset",
            "facility_type": "Manufacture",
            "support_email": "support@macclesfield.com",
            "support_phone": "123 456 789",
        },
    },
}
REQUEST_EXISTS_KWARGS_LOCATION_SIMPLE_HASH = {
    "json": {
        "behaviours": ASSET_BEHAVIOURS,
        "proof_mechanism": ProofMechanism.SIMPLE_HASH.name,
        "attributes": {
            "arc_display_name": ASSET_NAME,
            "arc_namespace": "namespace",
            "arc_firmware_version": "1.0",
            "arc_serial_number": "vtl-x4-07",
            "arc_description": "Traffic flow control light at A603 North East",
            "arc_display_type": "Traffic light with violation camera",
            "some_custom_attribute": "value",
            "arc_home_location_identity": f"{LOCATIONS_LABEL}/xxxxxxxx",
        },
    },
    "headers": {
        "authorization": "Bearer authauthauth",
    },
    "verify": True,
}
RESPONSE_EXISTS_LOCATION = {
    "identity": IDENTITY,
    "behaviours": ASSET_BEHAVIOURS,
    "attributes": {
        "arc_display_name": ASSET_NAME,
        "arc_namespace": "namespace",
        "arc_firmware_version": "1.0",
        "arc_serial_number": "vtl-x4-07",
        "arc_description": "Traffic flow control light at A603 North East",
        "arc_display_type": "Traffic light with violation camera",
        "some_custom_attribute": "value",
        "arc_home_location_identity": f"{LOCATIONS_LABEL}/xxxxxxxx",
    },
    "confirmation_status": "CONFIRMED",
    "tracked": "TRACKED",
}
RESPONSE_LOCATION = {
    "identity": f"{LOCATIONS_LABEL}/xxxxxxxx",
    "display_name": "Macclesfield, Cheshire",
    "description": "Manufacturing site, North West England, Macclesfield, Cheshire",
    "latitude": "53.2546799",
    "longitude": "-2.1213956,14.54",
    "attributes": {
        "director": "John Smith",
        "address": "Bridgewater, Somerset",
        "facility_type": "Manufacture",
        "support_email": "support@macclesfield.com",
        "support_phone": "123 456 789",
    },
}
# case 5 create if not exists with location identity
REQUEST_EXISTS_LOCATION_IDENTITY_SIMPLE_HASH = {
    "selector": [
        {
            "attributes": [
                "arc_display_name",
                "arc_namespace",
            ]
        },
    ],
    "behaviours": ASSET_BEHAVIOURS,
    "proof_mechanism": ProofMechanism.SIMPLE_HASH.name,
    "attributes": {
        "arc_display_name": ASSET_NAME,
        "arc_namespace": "namespace",
        "arc_firmware_version": "1.0",
        "arc_serial_number": "vtl-x4-07",
        "arc_description": "Traffic flow control light at A603 North East",
        "arc_display_type": "Traffic light with violation camera",
        "some_custom_attribute": "value",
    },
    "location": {
        "identity": f"{LOCATIONS_LABEL}/xxxxxxxx",
    },
}

# ---------------

REQUEST_FIXTURES_SIMPLE_HASH = {
    "behaviours": ASSET_BEHAVIOURS,
    "proof_mechanism": ProofMechanism.SIMPLE_HASH.name,
    "attributes": ATTRS_FIXTURES,
}
REQUEST_FIXTURES_KWARGS_SIMPLE_HASH = {
    "json": REQUEST_FIXTURES_SIMPLE_HASH,
    "headers": {
        "authorization": "Bearer authauthauth",
    },
    "verify": True,
}

RESPONSE_FIXTURES = {
    "identity": IDENTITY,
    "behaviours": ASSET_BEHAVIOURS,
    "attributes": ATTRS_FIXTURES,
    "confirmation_status": "CONFIRMED",
}
RESPONSE_NO_ATTACHMENTS = {
    "identity": IDENTITY,
    "behaviours": ASSET_BEHAVIOURS,
    "attributes": ATTRS_NO_ATTACHMENTS,
    "confirmation_status": "CONFIRMED",
}
RESPONSE_NO_CONFIRMATION = {
    "identity": IDENTITY,
    "behaviours": ASSET_BEHAVIOURS,
    "attributes": ATTRS,
}
RESPONSE_PENDING = {
    "identity": IDENTITY,
    "behaviours": ASSET_BEHAVIOURS,
    "attributes": ATTRS,
    "confirmation_status": "PENDING",
}
RESPONSE_FAILED = {
    "identity": IDENTITY,
    "behaviours": ASSET_BEHAVIOURS,
    "attributes": ATTRS,
    "confirmation_status": "FAILED",
}


class TestAssetsBase(TestCase):
    """
    Test Archivist Assets Base
    """

    maxDiff = None

    def setUp(self):
        self.arch = Archivist("url", "authauthauth", max_time=1)

    def tearDown(self):
        self.arch.close()


class TestAssetsBaseConfirm(TestCase):
    """
    Test Archivist Assets Base with expected confirmation
    """

    maxDiff = None

    def setUp(self):
        self.arch = Archivist("url", "authauthauth", max_time=30)

    def tearDown(self):
        self.arch.close()
