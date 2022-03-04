"""
Test archivist
"""

from unittest import TestCase

from archivist.archivist import Archivist
from archivist.assets import BEHAVIOURS
from archivist.constants import (
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
    "arc_display_name": "arc_primary_image",
    "arc_attachment_identity": "blobs/87b1a84c-1c6f-442b-923e-a97516f4d275",
    "arc_hash_alg": "SHA256",
    "arc_hash_value": "246c316e2cd6971ce5c83a3e61f9880fa6e2f14ae2976ee03500eb282fd03a60",
}
SECONDARY_IMAGE = {
    "arc_display_name": "arc_secondary_image",
    "arc_attachment_identity": "blobs/87b1a84c-1c6f-442b-923e-a97516f4d275",
    "arc_hash_alg": "SHA256",
    "arc_hash_value": "246c316e2cd6971ce5c83a3e61f9880fa6e2f14ae2976ee03500eb282fd03a60",
}
TERTIARY_IMAGE = {
    "arc_attachment_identity": "blobs/87b1a84c-1c6f-442b-923e-a97516f4d275",
    "arc_hash_alg": "SHA256",
    "arc_hash_value": "246c316e2cd6971ce5c83a3e61f9880fa6e2f14ae2976ee03500eb282fd03a60",
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
PROPS = {
    "proof_mechanism": ProofMechanism.SIMPLE_HASH.name,
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
REQUEST = {
    "behaviours": BEHAVIOURS,
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
REQUEST_KWARGS = {
    "json": {
        "behaviours": BEHAVIOURS,
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
    "behaviours": BEHAVIOURS,
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
REQUEST_EXISTS = {
    "selector": [
        {
            "attributes": [
                "arc_display_name",
                "arc_namespace",
            ]
        },
    ],
    "behaviours": BEHAVIOURS,
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
REQUEST_EXISTS_KWARGS = {
    "json": {
        "behaviours": BEHAVIOURS,
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
    "behaviours": BEHAVIOURS,
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
REQUEST_EXISTS_ATTACHMENTS = {
    "selector": [
        {
            "attributes": [
                "arc_display_name",
                "arc_namespace",
            ]
        },
    ],
    "behaviours": BEHAVIOURS,
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
    ],
}
REQUEST_EXISTS_KWARGS_ATTACHMENTS = {
    "json": {
        "behaviours": BEHAVIOURS,
        "proof_mechanism": ProofMechanism.SIMPLE_HASH.name,
        "attributes": {
            "arc_display_name": ASSET_NAME,
            "arc_namespace": "namespace",
            "arc_firmware_version": "1.0",
            "arc_serial_number": "vtl-x4-07",
            "arc_description": "Traffic flow control light at A603 North East",
            "arc_display_type": "Traffic light with violation camera",
            "some_custom_attribute": "value",
            "arc_attachments": [
                {
                    "arc_attachment_identity": f"{ATTACHMENTS_LABEL}/xxxxxxxx",
                    "arc_display_name": "arc_primary_image",
                    "arc_hash_alg": "SHA256",
                    "arc_hash_value": (
                        "246c316e2cd6971ce5c83a3e61f9"
                        "880fa6e2f14ae2976ee03500eb282fd03a60"
                    ),
                },
            ],
        },
    },
    "headers": {
        "authorization": "Bearer authauthauth",
    },
    "verify": True,
}
RESPONSE_ATTACHMENTS = {
    "arc_attachment_identity": f"{ATTACHMENTS_LABEL}/xxxxxxxx",
    "arc_display_name": "arc_primary_image",
    "arc_hash_alg": "SHA256",
    "arc_hash_value": "246c316e2cd6971ce5c83a3e61f9880fa6e2f14ae2976ee03500eb282fd03a60",
}
RESPONSE_EXISTS_ATTACHMENTS = {
    "identity": IDENTITY,
    "behaviours": BEHAVIOURS,
    "attributes": {
        "arc_namespace": "namespace",
        "arc_firmware_version": "1.0",
        "arc_serial_number": "vtl-x4-07",
        "arc_description": "Traffic flow control light at A603 North East",
        "arc_display_type": "Traffic light with violation camera",
        "some_custom_attribute": "value",
        "arc_display_name": ASSET_NAME,
        "arc_attachments": [
            {
                "arc_attachment_identity": "blobs/87b1a84c-1c6f-442b-923e-a97516f4d275",
                "arc_display_name": "arc_primary_image",
                "arc_hash_alg": "SHA256",
                "arc_hash_value": (
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
REQUEST_EXISTS_LOCATION = {
    "selector": [
        {
            "attributes": [
                "arc_display_name",
                "arc_namespace",
            ]
        },
    ],
    "behaviours": BEHAVIOURS,
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
REQUEST_EXISTS_KWARGS_LOCATION = {
    "json": {
        "behaviours": BEHAVIOURS,
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
    "behaviours": BEHAVIOURS,
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

# ---------------

REQUEST_FIXTURES = {
    "behaviours": BEHAVIOURS,
    "proof_mechanism": ProofMechanism.SIMPLE_HASH.name,
    "attributes": ATTRS_FIXTURES,
}
REQUEST_FIXTURES_KWARGS = {
    "json": REQUEST_FIXTURES,
    "headers": {
        "authorization": "Bearer authauthauth",
    },
    "verify": True,
}

RESPONSE_FIXTURES = {
    "identity": IDENTITY,
    "behaviours": BEHAVIOURS,
    "attributes": ATTRS_FIXTURES,
    "confirmation_status": "CONFIRMED",
}
RESPONSE_NO_ATTACHMENTS = {
    "identity": IDENTITY,
    "behaviours": BEHAVIOURS,
    "attributes": ATTRS_NO_ATTACHMENTS,
    "confirmation_status": "CONFIRMED",
}
RESPONSE_NO_CONFIRMATION = {
    "identity": IDENTITY,
    "behaviours": BEHAVIOURS,
    "attributes": ATTRS,
}
RESPONSE_PENDING = {
    "identity": IDENTITY,
    "behaviours": BEHAVIOURS,
    "attributes": ATTRS,
    "confirmation_status": "PENDING",
}
RESPONSE_FAILED = {
    "identity": IDENTITY,
    "behaviours": BEHAVIOURS,
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
        self.arch = None
