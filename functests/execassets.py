"""
Test assets creation
"""

from copy import deepcopy
from os import environ
from unittest import TestCase

from archivist.archivist import Archivist
from archivist.storage_integrity import StorageIntegrity

# pylint: disable=fixme
# pylint: disable=missing-docstring
# pylint: disable=unused-variable

BEHAVIOURS = [
    "RecordEvidence",
    "Attachments",
]
ATTRS = {
    "arc_firmware_version": "1.0",
    "arc_serial_number": "vtl-x4-07",
    "arc_description": "Traffic flow control light at A603 North East",
    "arc_home_location_identity": "locations/115340cf-f39e-4d43-a2ee-8017d672c6c6",
    "arc_display_type": "Traffic light with violation camera",
    "some_custom_attribute": "value",
}


class TestAssetCreate(TestCase):
    """
    Test Archivist Asset Create method
    """

    maxDiff = None

    def setUp(cls):
        with open(environ["TEST_AUTHTOKEN"]) as fd:
            auth = fd.read().strip()
        cls.arch = Archivist(environ["TEST_ARCHIVIST"], auth=auth, verify=False)
        cls.attrs = deepcopy(ATTRS)

    def test_asset_create_tenant_storage(self):
        """
        Test asset creation on tenant storage
        """
        asset = self.arch.assets.create(
            BEHAVIOURS,
            self.attrs,
            confirm=True,
        )
        self.assertEqual(
            asset["storage_integrity"],
            StorageIntegrity.TENANT_STORAGE.name,
            msg="Incorrect asset storage integrity",
        )

    def test_asset_create_ledger(self):
        """
        Test asset creation on ledger
        """
        asset = self.arch.assets.create(
            BEHAVIOURS,
            self.attrs,
            storage_integrity=StorageIntegrity.LEDGER,
            confirm=True,
        )
        self.assertEqual(
            asset["storage_integrity"],
            StorageIntegrity.LEDGER.name,
            msg="Incorrect asset storage integrity",
        )
