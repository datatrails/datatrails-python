"""
Test storage integrity
"""

# pylint: disable=attribute-defined-outside-init
# pylint: disable=missing-docstring
# pylint: disable=too-few-public-methods

from unittest import TestCase

from archivist.storage_integrity import StorageIntegrity


class TestStorageIntegrity(TestCase):
    """
    Test storage integrity for archivist
    """

    def test_storage_integrity(self):
        """
        Test storage_integrity
        """
        self.assertEqual(StorageIntegrity.LEDGER.value, 1, msg="Incorrect value")
        self.assertEqual(StorageIntegrity.LEDGER.name, "LEDGER", msg="Incorrect value")
        self.assertEqual(
            StorageIntegrity.TENANT_STORAGE.value, 2, msg="Incorrect value"
        )
        self.assertEqual(
            StorageIntegrity.TENANT_STORAGE.name,
            "TENANT_STORAGE",
            msg="Incorrect value",
        )
