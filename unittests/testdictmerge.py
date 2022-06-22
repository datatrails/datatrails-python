"""
Test dictmerge
"""

# pylint: disable=missing-docstring
# pylint: disable=protected-access
# pylint: disable=too-few-public-methods

from unittest import TestCase

from archivist import dictmerge


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
        test_data_assets = [
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
                            "arc_hash_value": "b6ec2d1829b8fbf0d58c4f4d87a56a68b16236ef173c7b8b23713078010049ff",
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
        ]
        self.assertEqual(
            len(dictmerge.assets_ext_attr(test_data_assets)),
            1,
            msg="assets_ext_attr returns incorrect result",
        )

    def test_attachment_identities_assets(self):
        test_data_assets_w_attachment = [
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
                            "arc_hash_value": "b6ec2d1829b8fbf0d58c4f4d87a56a68b16236ef173c7b8b23713078010049ff",
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
        self.assertEqual(
            len(dictmerge.attachment_identities_assets(test_data_assets_w_attachment)),
            1,
            msg="attachment_identities_assets returns incorrect result",
        )

    def test_events_ext_attr(self):
        test_data_events = [
            {
                "identity": "assets/2ae491bd-ac42-406f-8bf5-fa7d25cd53e7/events/25606a10-42c0-429c-ae94-e2df7ee8a5dc",
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
                "identity": "assets/525e4c24-711c-457d-b528-f9a4879f0759/events/401b83eb-3da7-467f-942d-cba33203a129",
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
                            "arc_hash_value": "b6ec2d1829b8fbf0d58c4f4d87a56a68b16236ef173c7b8b23713078010049ff",
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
        ]
        self.assertEqual(
            len(dictmerge.events_ext_attr(test_data_events)),
            1,
            msg="events_ext_attr returns incorrect result",
        )

    def test_attachment_identities_events(self):
        test_data_event_w_attachment = [
            {
                "identity": "assets/2ae491bd-ac42-406f-8bf5-fa7d25cd53e7/events/5f299e54-93cd-406b-943f-1c1717612127",
                "asset_identity": "assets/2ae491bd-ac42-406f-8bf5-fa7d25cd53e7",
                "event_attributes": {
                    "arc_attachments": [
                        {
                            "arc_display_name": "Inspection Standards",
                            "arc_hash_alg": "SHA256",
                            "arc_hash_value": "b6ec2d1829b8fbf0d58c4f4d87a56a68b16236ef173c7b8b23713078010049ff",
                            "arc_attachment_identity": "blobs/1718b2c9-8764-4733-8926-4688c7ad192e",
                        }
                    ],
                    "arc_description": "Inspection Event",
                    "arc_display_type": "Inspection",
                    "Cargo": "Rare Metals",
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
        self.assertEqual(
            len(dictmerge.events_ext_attr(test_data_event_w_attachment)),
            1,
            msg="attachment_identities_events returns incorrect result",
        )

    def test_level_1_sanitization(self):
        dct_1 = {
            "arc_display_type": "Test",
            "arc_description": "Asset created for testing",
            "arc_display_name": "Test Asset",
        }
        self.assertEqual(
            dictmerge.level_1_sanitization(dct_1),
            dct_1,
            msg="level_1_sanitization returns incorrect result",
        )
        dct_2 = {
            "arc_display_type": "Test",
            "custom_attribute": "custom_value",
            "arc_description": "Asset created for testing",
            "arc_display_name": "Test Asset",
        }
        self.assertNotEqual(
            dictmerge.level_1_sanitization(dct_2),
            dct_2,
            msg="level_1_sanitization returns incorrect result",
        )

    def test_level_2_sanitization(self):
        dct_1 = {
            "arc_display_type": "Test",
            "custom_attribute": "custom_value",
            "arc_description": "Asset created for testing",
            "arc_display_name": "Test Asset",
        }
        self.assertNotEqual(
            dictmerge.level_2_sanitization(dct_1),
            dct_1,
            msg="level_2_sanitization returns incorrect result",
        )
        self.assertRegex(
            str(dictmerge.level_2_sanitization(dct_1).values()),
            r"#",
            msg="values not properly redacted in level_2_sanitization",
        )

    def test_level_3_sanitization(self):
        dct_1 = {
            "arc_display_type": "Test",
            "custom_attribute": "custom_value",
            "arc_description": "Asset created for testing",
            "arc_display_name": "Test Asset",
        }
        self.assertNotEqual(
            dictmerge.level_3_sanitization(dct_1),
            dct_1,
            msg="level_3_sanitization returns incorrect result",
        )
        self.assertRegex(
            str(dictmerge.level_3_sanitization(dct_1).values()),
            r"#",
            msg="values not properly redacted in level_3_sanitization",
        )

    def test_level_4_sanitization(self):
        dct_1 = {
            "arc_display_type": "Test",
            "custom_attribute": "custom_value",
            "arc_description": "Asset created for testing",
            "arc_display_name": "Test Asset",
        }
        self.assertNotEqual(
            dictmerge.level_4_sanitization(dct_1),
            dct_1,
            msg="level_4_sanitization returns incorrect result",
        )
        self.assertRegex(
            str(dictmerge.level_4_sanitization(dct_1).keys()),
            r"#",
            msg="keys not properly redacted in level_4_sanitization",
        )
        self.assertRegex(
            str(dictmerge.level_4_sanitization(dct_1).values()),
            r"#",
            msg="values not properly redacted in level_4_sanitization",
        )

    def test_level_5_sanitization(self):
        dct_1 = {
            "arc_display_type": "Test",
            "custom_attribute": "custom_value",
            "arc_description": "Asset created for testing",
            "arc_display_name": "Test Asset",
        }
        self.assertNotEqual(
            dictmerge.level_5_sanitization(dct_1),
            dct_1,
            msg="level_5_sanitization returns incorrect result",
        )
