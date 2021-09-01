"""
Test assets creation
"""

from copy import copy, deepcopy
from os import environ
from unittest import TestCase
from uuid import uuid4

from archivist.archivist import Archivist
from archivist.storage_integrity import StorageIntegrity

# pylint: disable=fixme
# pylint: disable=missing-docstring
# pylint: disable=unused-variable

ATTRS = {
    "arc_firmware_version": "1.0",
    "arc_serial_number": "vtl-x4-07",
    "arc_description": "Traffic flow control light at A603 North East",
    "some_custom_attribute": "value",
}


class TestAssetCreate(TestCase):
    """
    Test Archivist Asset Create method
    """

    maxDiff = None

    @classmethod
    def setUpClass(cls):
        with open(environ["TEST_AUTHTOKEN_FILENAME"]) as fd:
            auth = fd.read().strip()
        cls.arch = Archivist(
            environ["TEST_ARCHIVIST"], auth=auth, verify=False, max_time=300
        )
        cls.attrs = deepcopy(ATTRS)
        cls.traffic_light = deepcopy(ATTRS)
        cls.traffic_light["arc_display_type"] = "Traffic light with violation camera"

    @classmethod
    def tearDownClass(cls):
        cls.arch = None
        cls.attrs = None
        cls.traffic_light = None

    def test_asset_create_tenant_storage(self):
        """
        Test asset creation on tenant storage
        """
        asset = self.arch.assets.create(
            attrs=self.traffic_light,
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
            props={
                "storage_integrity": StorageIntegrity.LEDGER.name,
            },
            attrs=self.traffic_light,
            confirm=True,
        )
        self.assertEqual(
            asset["storage_integrity"],
            StorageIntegrity.LEDGER.name,
            msg="Incorrect asset storage integrity",
        )

    def test_asset_create_with_fixtures(self):
        """
        Test creation with fixtures
        """
        # creates tenant_storage endpoint
        tenant_storage = copy(self.arch)
        tenant_storage.fixtures = {
            "assets": {
                "storage_integrity": StorageIntegrity.TENANT_STORAGE.name,
            },
        }

        # create traffic lights endpoint from tenant_storage
        traffic_lights = copy(tenant_storage)
        traffic_lights.fixtures = {
            "assets": {
                "attributes": {
                    "arc_display_type": "Traffic light with violation camera",
                    "arc_namespace": f"functests {uuid4()}",
                },
            },
        }
        traffic_light = traffic_lights.assets.create(
            attrs=self.attrs,
            confirm=True,
        )
        self.assertEqual(
            traffic_lights.assets.count(),
            1,
            msg="Incorrect number of traffic_lights",
        )

        # create fancy traffic lights endpoint from traffic lights
        fancy_traffic_lights = copy(traffic_lights)
        fancy_traffic_lights.fixtures = {
            "assets": {
                "attributes": {
                    "arc_namespace1": f"functests {uuid4()}",
                },
            },
        }
        fancy_traffic_light = fancy_traffic_lights.assets.create(
            attrs=self.attrs,
            confirm=True,
        )
        self.assertEqual(
            fancy_traffic_lights.assets.count(),
            1,
            msg="Incorrect number of fancy_traffic_lights",
        )
