"""
Test dictmerge
"""

# pylint: disable=missing-docstring
# pylint: disable=protected-access
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-locals

from unittest import TestCase

from archivist import dictmerge

ASSET_TEST_DATA = [
    {
        "identity": "assets/525e4c24-711c-457d-b528-f9a4879f0759",
        "behaviours": [
            "Builtin",
            "AssetCreator",
            "RecordEvidence",
            "Attachments",
        ],
        "attributes": {
            "arc_display_name": "Asset with attachment",
            "arc_display_type": "Nested attribute",
            "arc_attachments": [
                {
                    "arc_hash_value": (
                        "b6ec2d1829b8fbf0d58c4f4d87a56a68b16236ef173c7b8b23713078010049ff"
                    ),
                    "mime_type": "application/pdf",
                    "arc_attachment_identity": "blobs/ea4bcf42-2b72-4903-919b-b856443fc511",
                    "arc_display_name": "Inspection Standards",
                    "arc_hash_alg": "SHA256",
                }
            ],
            "arc_description": "Asset created for testing",
        },
        "confirmation_status": "CONFIRMED",
        "tracked": "TRACKED",
        "owner": "##########",
        "at_time": "2022-06-13T22:57:54Z",
        "storage_integrity": "TENANT_STORAGE",
        "proof_mechanism": "SIMPLE_HASH",
        "chain_id": "##########",
    },
    {
        "identity": "assets/976f03e8-458d-42fb-9cc4-720720ed648f",
        "behaviours": [
            "Builtin",
            "AssetCreator",
            "RecordEvidence",
            "Attachments",
        ],
        "attributes": {
            "arc_display_type": "Test",
            "Weight": "1192kg",
            "arc_description": "Asset created for testing",
            "arc_display_name": "Test Asset",
        },
        "confirmation_status": "CONFIRMED",
        "tracked": "TRACKED",
        "owner": "##########",
        "at_time": "2022-06-13T22:57:54Z",
        "storage_integrity": "TENANT_STORAGE",
        "proof_mechanism": "SIMPLE_HASH",
        "chain_id": "##########",
    },
    {
        "identity": "assets/976f03e8-458d-42fb-9cc4-720720ed648g",
        "behaviours": [
            "Builtin",
            "AssetCreator",
            "RecordEvidence",
            "Attachments",
        ],
        "attributes": {
            "arc_display_type": "Test",
            "arc_description": "Asset created for testing",
            "arc_display_name": "Test Asset",
            "arc_home_location_identity": "locations/141fba96-43c6-462b-b934-2110f6e94162",
        },
        "confirmation_status": "CONFIRMED",
        "tracked": "TRACKED",
        "owner": "##########",
        "at_time": "2022-06-13T22:57:54Z",
        "storage_integrity": "TENANT_STORAGE",
        "proof_mechanism": "SIMPLE_HASH",
        "chain_id": "##########",
    },
]

EXPECTED_ASSETS_EXT_ATTR = [
    {
        "identity": "assets/976f03e8-458d-42fb-9cc4-720720ed648f",
        "behaviours": [
            "Builtin",
            "AssetCreator",
            "RecordEvidence",
            "Attachments",
        ],
        "attributes": {
            "arc_display_type": "Test",
            "Weight": "1192kg",
            "arc_description": "Asset created for testing",
            "arc_display_name": "Test Asset",
        },
        "confirmation_status": "CONFIRMED",
        "tracked": "TRACKED",
        "owner": "##########",
        "at_time": "2022-06-13T22:57:54Z",
        "storage_integrity": "TENANT_STORAGE",
        "proof_mechanism": "SIMPLE_HASH",
        "chain_id": "##########",
    }
]

ASSET_WITH_ATTACHMENT = [
    {
        "identity": "assets/525e4c24-711c-457d-b528-f9a4879f0759",
        "behaviours": [
            "Builtin",
            "AssetCreator",
            "RecordEvidence",
            "Attachments",
        ],
        "attributes": {
            "arc_display_name": "Asset with attachment",
            "arc_display_type": "Nested attribute",
            "arc_attachments": [
                {
                    "arc_hash_value": (
                        "b6ec2d1829b8fbf0d58c4f4d87a56a68b16236ef173c7b8b23713078010049ff"
                    ),
                    "mime_type": "application/pdf",
                    "arc_attachment_identity": "blobs/ea4bcf42-2b72-4903-919b-b856443fc511",
                    "arc_display_name": "Inspection Standards",
                    "arc_hash_alg": "SHA256",
                }
            ],
            "arc_description": "Asset created for testing",
        },
        "confirmation_status": "CONFIRMED",
        "tracked": "TRACKED",
        "owner": "##########",
        "at_time": "2022-06-13T22:57:54Z",
        "storage_integrity": "TENANT_STORAGE",
        "proof_mechanism": "SIMPLE_HASH",
        "chain_id": "##########",
    }
]

EXPECTED_ASSETS_LOCATION = [
    {
        "identity": "assets/976f03e8-458d-42fb-9cc4-720720ed648g",
        "behaviours": [
            "Builtin",
            "AssetCreator",
            "RecordEvidence",
            "Attachments",
        ],
        "attributes": {
            "arc_display_type": "Test",
            "arc_description": "Asset created for testing",
            "arc_display_name": "Test Asset",
            "arc_home_location_identity": "locations/141fba96-43c6-462b-b934-2110f6e94162",
        },
        "confirmation_status": "CONFIRMED",
        "tracked": "TRACKED",
        "owner": "##########",
        "at_time": "2022-06-13T22:57:54Z",
        "storage_integrity": "TENANT_STORAGE",
        "proof_mechanism": "SIMPLE_HASH",
        "chain_id": "##########",
    }
]

EVENT_TEST_DATA = [
    {
        "identity": (
            "assets/2ae491bd-ac42-406f-8bf5-fa7d25cd53e7/"
            "events/25606a10-42c0-429c-ae94-e2df7ee8a5dc"
        ),
        "asset_identity": "assets/2ae491bd-ac42-406f-8bf5-fa7d25cd53e7",
        "event_attributes": {
            "test": "test",
            "arc_attachments": [],
            "arc_display_type": "test",
        },
        "asset_attributes": {"custom_asset": "private_information"},
        "operation": "Record",
        "behaviour": "RecordEvidence",
        "timestamp_declared": "2022-05-18T16:36:05Z",
        "timestamp_accepted": "2022-05-18T16:36:05Z",
        "timestamp_committed": "2022-05-18T16:36:05.308639394Z",
        "principal_declared": {
            "issuer": "local",
            "subject": "camrynjr@icloud.com",
            "display_name": "Camryn Carter",
            "email": "camrynjr@icloud.com",
        },
        "principal_accepted": {
            "issuer": "local",
            "subject": "camrynjr@icloud.com",
            "display_name": "Camryn Carter",
            "email": "camrynjr@icloud.com",
        },
        "confirmation_status": "CONFIRMED",
        "transaction_id": "",
        "block_number": 0,
        "transaction_index": 0,
        "from": "0xD71D6404F57a081637661F2DAac32Ca37047f240",
    },
    {
        "identity": (
            "assets/525e4c24-711c-457d-b528-f9a4879f0759/"
            "events/401b83eb-3da7-467f-942d-cba33203a129"
        ),
        "asset_identity": "assets/525e4c24-711c-457d-b528-f9a4879f0759",
        "event_attributes": {
            "arc_attachments": [],
            "arc_display_type": "Add attachment ",
        },
        "asset_attributes": {
            "arc_attachments": [
                {
                    "arc_attachment_identity": "blobs/ea4bcf42-2b72-4903-919b-b856443fc511",
                    "arc_display_name": "Inspection Standards",
                    "arc_hash_alg": "SHA256",
                    "arc_hash_value": (
                        "b6ec2d1829b8fbf0d58c4f4d87a56a68b16236ef173c7b8b23713078010049ff"
                    ),
                    "mime_type": "application/pdf",
                }
            ]
        },
        "operation": "Record",
        "behaviour": "RecordEvidence",
        "timestamp_declared": "2022-06-01T18:02:37Z",
        "timestamp_accepted": "2022-06-01T18:02:37Z",
        "timestamp_committed": "2022-06-01T18:02:37.610782126Z",
        "principal_declared": {
            "issuer": "local",
            "subject": "camrynjr@icloud.com",
            "display_name": "Camryn Carter",
            "email": "camrynjr@icloud.com",
        },
        "principal_accepted": {
            "issuer": "local",
            "subject": "camrynjr@icloud.com",
            "display_name": "Camryn Carter",
            "email": "camrynjr@icloud.com",
        },
        "confirmation_status": "CONFIRMED",
        "transaction_id": "",
        "block_number": 0,
        "transaction_index": 0,
        "from": "0xD71D6404F57a081637661F2DAac32Ca37047f240",
    },
    {
        "identity": (
            "assets/2ae491bd-ac42-406f-8bf5-fa7d25cd53e8/"
            "events/5f299e54-93cd-406b-943f-1c1717612128"
        ),
        "asset_identity": "assets/2ae491bd-ac42-406f-8bf5-fa7d25cd53e8",
        "event_attributes": {
            "arc_attachments": [
                {
                    "arc_display_name": "Inspection Standards",
                    "arc_hash_alg": "SHA256",
                    "arc_hash_value": (
                        "b6ec2d1829b8fbf0d58c4f4d87a56a68b16236ef173c7b8b23713078010049ff"
                    ),
                    "arc_attachment_identity": "blobs/1718b2c9-8764-4733-8926-4688c7ad192e",
                }
            ],
            "arc_description": "Inspection Event",
            "arc_display_type": "Inspection",
        },
        "asset_attributes": {"Weight": "1192kg"},
        "operation": "Record",
        "behaviour": "RecordEvidence",
        "timestamp_declared": "2022-05-16T18:18:31Z",
        "timestamp_accepted": "2022-05-16T18:18:31Z",
        "timestamp_committed": "2022-05-16T18:18:31.942593153Z",
        "principal_declared": {
            "issuer": "https://app.rkvst.io/appidpv1",
            "subject": "e1da3214-f5e2-4ec9-9664-80881ed5ccd2",
            "display_name": "Camryn Carter",
            "email": "",
        },
        "principal_accepted": {
            "issuer": "https://app.rkvst.io/appidpv1",
            "subject": "e1da3214-f5e2-4ec9-9664-80881ed5ccd2",
            "display_name": "Camryn Carter",
            "email": "",
        },
        "confirmation_status": "CONFIRMED",
        "transaction_id": "",
        "block_number": 0,
        "transaction_index": 0,
        "from": "0xD71D6404F57a081637661F2DAac32Ca37047f240",
    },
]

EXPECTED_EVENTS_EXT_ATTR = [
    {
        "identity": (
            "assets/2ae491bd-ac42-406f-8bf5-fa7d25cd53e7/"
            "events/25606a10-42c0-429c-ae94-e2df7ee8a5dc"
        ),
        "asset_identity": "assets/2ae491bd-ac42-406f-8bf5-fa7d25cd53e7",
        "event_attributes": {
            "test": "test",
            "arc_attachments": [],
            "arc_display_type": "test",
        },
        "asset_attributes": {"custom_asset": "private_information"},
        "operation": "Record",
        "behaviour": "RecordEvidence",
        "timestamp_declared": "2022-05-18T16:36:05Z",
        "timestamp_accepted": "2022-05-18T16:36:05Z",
        "timestamp_committed": "2022-05-18T16:36:05.308639394Z",
        "principal_declared": {
            "issuer": "local",
            "subject": "camrynjr@icloud.com",
            "display_name": "Camryn Carter",
            "email": "camrynjr@icloud.com",
        },
        "principal_accepted": {
            "issuer": "local",
            "subject": "camrynjr@icloud.com",
            "display_name": "Camryn Carter",
            "email": "camrynjr@icloud.com",
        },
        "confirmation_status": "CONFIRMED",
        "transaction_id": "",
        "block_number": 0,
        "transaction_index": 0,
        "from": "0xD71D6404F57a081637661F2DAac32Ca37047f240",
    }
]

EVENT_WITH_ATTACHMENT = [
    {
        "identity": (
            "assets/2ae491bd-ac42-406f-8bf5-fa7d25cd53e8/"
            "events/5f299e54-93cd-406b-943f-1c1717612128"
        ),
        "asset_identity": "assets/2ae491bd-ac42-406f-8bf5-fa7d25cd53e8",
        "event_attributes": {
            "arc_attachments": [
                {
                    "arc_display_name": "Inspection Standards",
                    "arc_hash_alg": "SHA256",
                    "arc_hash_value": (
                        "b6ec2d1829b8fbf0d58c4f4d87a56a68b16236ef173c7b8b23713078010049ff"
                    ),
                    "arc_attachment_identity": "blobs/1718b2c9-8764-4733-8926-4688c7ad192e",
                }
            ],
            "arc_description": "Inspection Event",
            "arc_display_type": "Inspection",
        },
        "asset_attributes": {"Weight": "1192kg"},
        "operation": "Record",
        "behaviour": "RecordEvidence",
        "timestamp_declared": "2022-05-16T18:18:31Z",
        "timestamp_accepted": "2022-05-16T18:18:31Z",
        "timestamp_committed": "2022-05-16T18:18:31.942593153Z",
        "principal_declared": {
            "issuer": "https://app.rkvst.io/appidpv1",
            "subject": "e1da3214-f5e2-4ec9-9664-80881ed5ccd2",
            "display_name": "Camryn Carter",
            "email": "",
        },
        "principal_accepted": {
            "issuer": "https://app.rkvst.io/appidpv1",
            "subject": "e1da3214-f5e2-4ec9-9664-80881ed5ccd2",
            "display_name": "Camryn Carter",
            "email": "",
        },
        "confirmation_status": "CONFIRMED",
        "transaction_id": "",
        "block_number": 0,
        "transaction_index": 0,
        "from": "0xD71D6404F57a081637661F2DAac32Ca37047f240",
    }
]

EVENT_WITH_ASSET_ATTACHMENT = [
    {
        "identity": (
            "assets/525e4c24-711c-457d-b528-f9a4879f0759/"
            "events/401b83eb-3da7-467f-942d-cba33203a129"
        ),
        "asset_identity": "assets/525e4c24-711c-457d-b528-f9a4879f0759",
        "event_attributes": {
            "arc_attachments": [],
            "arc_display_type": "Add attachment ",
        },
        "asset_attributes": {
            "arc_attachments": [
                {
                    "arc_hash_alg": "SHA256",
                    "arc_hash_value": (
                        "b6ec2d1829b8fbf0d58c4f4d87a56a68b16236ef173c7b8b23713078010049ff"
                    ),
                    "mime_type": "application/pdf",
                    "arc_attachment_identity": "blobs/ea4bcf42-2b72-4903-919b-b856443fc511",
                    "arc_display_name": "Inspection Standards",
                }
            ]
        },
        "operation": "Record",
        "behaviour": "RecordEvidence",
        "timestamp_declared": "2022-06-01T18:02:37Z",
        "timestamp_accepted": "2022-06-01T18:02:37Z",
        "timestamp_committed": "2022-06-01T18:02:37.610782126Z",
        "principal_declared": {
            "issuer": "local",
            "subject": "camrynjr@icloud.com",
            "display_name": "Camryn Carter",
            "email": "camrynjr@icloud.com",
        },
        "principal_accepted": {
            "issuer": "local",
            "subject": "camrynjr@icloud.com",
            "display_name": "Camryn Carter",
            "email": "camrynjr@icloud.com",
        },
        "confirmation_status": "CONFIRMED",
        "transaction_id": "",
        "block_number": 0,
        "transaction_index": 0,
        "from": "0xD71D6404F57a081637661F2DAac32Ca37047f240",
    }
]


class TestDictMerge(TestCase):
    """
    Test dictmerge
    """

    def test_dictmerge(self):
        """
        Test dictmerge
        """
        self.assertEqual(
            dictmerge._deepmerge(None, None),
            {},
            msg="Dictmerge returns incorrect result",
        )
        self.assertEqual(
            dictmerge._deepmerge({"key": "value"}, None),
            {"key": "value"},
            msg="Dictmerge returns incorrect result",
        )
        self.assertEqual(
            dictmerge._deepmerge(None, {"key": "value"}),
            {"key": "value"},
            msg="Dictmerge returns incorrect result",
        )
        self.assertEqual(
            dictmerge._deepmerge(
                {"key": "value"},
                {"key1": "value1"},
            ),
            {"key": "value", "key1": "value1"},
            msg="Dictmerge returns incorrect result",
        )
        self.assertEqual(
            dictmerge._deepmerge(
                {"key": "value", "sub": {"subkey": "subvalue"}},
                {"key1": "value1", "sub1": {"subkey1": "subvalue1"}},
            ),
            {
                "key": "value",
                "sub": {"subkey": "subvalue"},
                "key1": "value1",
                "sub1": {"subkey1": "subvalue1"},
            },
            msg="Dictmerge returns incorrect result",
        )

    def test_dotdict(self):
        """
        Test dotdict
        """
        self.assertIsNone(
            dictmerge._dotdict(None),
            msg="Dotdict returns incorrect result",
        )
        self.assertEqual(
            dictmerge._dotdict({}),
            {},
            msg="Dotdict returns incorrect result",
        )
        self.assertEqual(
            dictmerge._dotdict({"key1": "value1"}),
            {"key1": "value1"},
            msg="Dotdict returns incorrect result",
        )
        self.assertEqual(
            dictmerge._dotdict({"key": "value", "sub": {"subkey": "subvalue"}}),
            {"key": "value", "sub.subkey": "subvalue"},
            msg="Dotdict returns incorrect result",
        )

    def test_assets_ext_attr(self):
        self.assertEqual(
            len(dictmerge.assets_ext_attr(ASSET_TEST_DATA)),
            1,
            msg="assets_ext_attr returns incorrect length",
        )
        self.assertEqual(
            dictmerge.assets_ext_attr(ASSET_TEST_DATA),
            EXPECTED_ASSETS_EXT_ATTR,
            msg="assets_ext_attr returning incorrect asset(s)",
        )

    def test_events_ext_attr(self):
        self.assertEqual(
            len(dictmerge.events_ext_attr(EVENT_TEST_DATA)),
            1,
            msg="events_ext_attr returns incorrect length",
        )
        self.assertEqual(
            dictmerge.events_ext_attr(EVENT_TEST_DATA),
            EXPECTED_EVENTS_EXT_ATTR,
            msg="events_ext_attr returning incorrect event(s)",
        )

    def test_assets_location(self):
        self.assertEqual(
            len(dictmerge.assets_location(ASSET_TEST_DATA)),
            1,
            msg="assets_location returning incorrect number of assets",
        )
        self.assertEqual(
            dictmerge.assets_location(ASSET_TEST_DATA),
            EXPECTED_ASSETS_LOCATION,
            msg="assets_location returning incorrect assets",
        )

    def test_assets_attachment(self):
        self.assertEqual(
            len(dictmerge.assets_attachment(ASSET_TEST_DATA)),
            1,
            msg="assets_attachment returning incorrect number of assets",
        )
        self.assertEqual(
            dictmerge.assets_attachment(ASSET_TEST_DATA),
            ASSET_WITH_ATTACHMENT,
            msg="assets_attachment returning incorrect assets",
        )

    def test_events_attachment(self):
        self.assertEqual(
            len(dictmerge.events_attachment(EVENT_WITH_ATTACHMENT)),
            1,
            msg="events_attachment returns incorrect length",
        )
        self.assertEqual(
            len(dictmerge.events_attachment(EVENT_WITH_ASSET_ATTACHMENT)),
            0,
            msg="events_attachment counting events with asset attachments",
        )
        self.assertEqual(
            dictmerge.events_attachment(EVENT_TEST_DATA),
            EVENT_WITH_ATTACHMENT,
            msg="events_attachment returning incorrect events",
        )
