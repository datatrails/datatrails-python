"""
Test assets creation
"""

from copy import copy, deepcopy
import json
from os import environ
from unittest import skip, TestCase
from uuid import uuid4

from archivist.archivist import Archivist
from archivist.proof_mechanism import ProofMechanism

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
        with open(environ["TEST_AUTHTOKEN_FILENAME"], encoding="utf-8") as fd:
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

    def test_asset_create_simple_hash(self):
        """
        Test asset creation uses simple hash proof mechanism
        """
        asset = self.arch.assets.create(
            attrs=self.traffic_light,
            confirm=True,
        )
        self.assertEqual(
            asset["proof_mechanism"],
            ProofMechanism.SIMPLE_HASH.name,
            msg="Incorrect asset proof mechanism",
        )

    @skip("takes too long")
    def test_asset_create_khipu(self):
        """
        Test asset creation using khipu proof mechanism
        """
        asset = self.arch.assets.create(
            props={
                "proof_mechanism": ProofMechanism.KHIPU.name,
            },
            attrs=self.traffic_light,
            confirm=True,
        )
        self.assertEqual(
            asset["proof_mechanism"],
            ProofMechanism.KHIPU.name,
            msg="Incorrect asset proof mechanism",
        )

    def test_asset_create_with_fixtures(self):
        """
        Test creation with fixtures
        """
        # creates simple_hash endpoint
        simple_hash = copy(self.arch)
        simple_hash.fixtures = {
            "assets": {
                "proof_mechanism": ProofMechanism.SIMPLE_HASH.name,
            },
        }

        # create traffic lights endpoint from simple_hash
        traffic_lights = copy(simple_hash)
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

    def test_asset_create_event(self):
        """
        Test list
        """
        # get identity of first asset
        identity = None
        for asset in self.arch.assets.list():
            print("asset", json.dumps(asset, sort_keys=True, indent=4))
            identity = asset["identity"]
            break

        self.assertIsNotNone(
            identity,
            msg="Identity is None",
        )

        # different behaviours are also different.
        props = {
            "operation": "Record",
            # This event is used to record evidence.
            "behaviour": "RecordEvidence",
            # Optional Client-claimed time at which the maintenance was performed
            "timestamp_declared": "2019-11-27T14:44:19Z",
            # Optional Client-claimed identity of person performing the operation
            "principal_declared": {
                "issuer": "idp.synsation.io/1234",
                "subject": "phil.b",
                "email": "phil.b@synsation.io",
            },
        }
        attrs = {
            # Required Details of the RecordEvidence request
            "arc_description": "Safety conformance approved for version 1.6.",
            # Required The evidence to be retained in the asset history
            "arc_evidence": "DVA Conformance Report attached",
            # Example Client can add any additional information in further attributes,
            # including free text or attachments
            "conformance_report": "blobs/e2a1d16c-03cd-45a1-8cd0-690831df1273",
        }

        event = self.arch.events.create(
            identity, props=props, attrs=attrs, confirm=True
        )
        print("event", json.dumps(event, sort_keys=True, indent=4))
