"""
Test applications
"""
from copy import deepcopy
from json import dumps as json_dumps
from os import environ
from time import sleep
from unittest import TestCase
from uuid import uuid4

from archivist.archivist import Archivist
from archivist.logger import set_logger
from archivist.proof_mechanism import ProofMechanism

# pylint: disable=fixme
# pylint: disable=missing-docstring
# pylint: disable=unused-variable

DISPLAY_NAME = "Application display name"
CUSTOM_CLAIMS = {
    "serial_number": "TL1000000101",
    "has_cyclist_light": "true",
}

ATTRS = {
    "arc_firmware_version": "1.0",
    "arc_serial_number": "vtl-x4-07",
    "arc_description": "Traffic flow control light at A603 North East",
    "some_custom_attribute": "value",
}

if "TEST_DEBUG" in environ and environ["TEST_DEBUG"]:
    set_logger(environ["TEST_DEBUG"])


class TestApplications(TestCase):
    """
    Test Archivist Applications Create method
    """

    maxDiff = None

    @classmethod
    def setUpClass(cls):
        with open(environ["TEST_AUTHTOKEN_FILENAME"], encoding="utf-8") as fd:
            auth = fd.read().strip()
        cls.arch = Archivist(environ["TEST_ARCHIVIST"], auth, verify=False)
        cls.display_name = f"{DISPLAY_NAME} {uuid4()}"

    def test_applications_create(self):
        """
        Test application creation
        """
        application = self.arch.applications.create(
            self.display_name,
            CUSTOM_CLAIMS,
        )
        print("create application", json_dumps(application, indent=4))
        self.assertEqual(
            application["display_name"],
            self.display_name,
            msg="Incorrect display name",
        )

    def test_applications_update(self):
        """
        Test application update
        """
        application = self.arch.applications.create(
            self.display_name,
            CUSTOM_CLAIMS,
        )
        print("create application", json_dumps(application, indent=4))
        self.assertEqual(
            application["display_name"],
            self.display_name,
            msg="Incorrect display name",
        )
        application = self.arch.applications.update(
            application["identity"],
            display_name=self.display_name,
            custom_claims=CUSTOM_CLAIMS,
        )
        print("update application", json_dumps(application, indent=4))

    def test_applications_delete(self):
        """
        Test application delete
        """
        application = self.arch.applications.create(
            self.display_name,
            CUSTOM_CLAIMS,
        )
        print("create application", json_dumps(application, indent=4))
        self.assertEqual(
            application["display_name"],
            self.display_name,
            msg="Incorrect display name",
        )
        application = self.arch.applications.delete(
            application["identity"],
        )
        print("delete application", json_dumps(application, indent=4))
        self.assertEqual(
            application,
            {},
            msg="Incorrect application",
        )

    def test_applications_regenerate(self):
        """
        Test application regenerate
        """
        application = self.arch.applications.create(
            self.display_name,
            CUSTOM_CLAIMS,
        )
        print("create application", json_dumps(application, indent=4))
        self.assertEqual(
            application["display_name"],
            self.display_name,
            msg="Incorrect display name",
        )
        application = self.arch.applications.regenerate(
            application["identity"],
        )
        print("regenerate application", json_dumps(application, indent=4))

    def test_applications_list(self):
        """
        Test application list
        """
        applications = list(self.arch.applications.list(display_name=self.display_name))
        self.assertGreater(
            len(applications),
            0,
            msg="Incorrect display name",
        )
        for application in applications:
            print("application", json_dumps(application, indent=4))

        for application in applications:
            self.assertGreater(
                len(application["display_name"]),
                0,
                msg="Incorrect display name",
            )
            self.assertEqual(
                application["display_name"],
                self.display_name,
                msg="Incorrect display name",
            )

    def test_appidp_token(self):
        """
        Test appidp token
        """
        application = self.arch.applications.create(
            self.display_name,
            CUSTOM_CLAIMS,
        )
        print("create application", json_dumps(application, indent=4))
        self.assertEqual(
            application["display_name"],
            self.display_name,
            msg="Incorrect display name",
        )
        appidp = self.arch.appidp.token(
            application["client_id"],
            application["credentials"][0]["secret"],
        )
        print("appidp", json_dumps(appidp, indent=4))

    def test_archivist_token(self):
        """
        Test archivist with client id/secret
        """
        application = self.arch.applications.create(
            self.display_name,
            CUSTOM_CLAIMS,
        )
        print("create application", json_dumps(application, indent=4))
        self.assertEqual(
            application["display_name"],
            self.display_name,
            msg="Incorrect display name",
        )

        # archivist using app registration
        new_arch = Archivist(
            environ["TEST_ARCHIVIST"],
            (application["client_id"], application["credentials"][0]["secret"]),
            verify=False,
        )

        # now we create an asset and add events 10 times with a 60s sleep
        # this should trigger a token refresh
        traffic_light = deepcopy(ATTRS)
        traffic_light["arc_display_type"] = "Traffic light with violation camera"
        asset = new_arch.assets.create(
            attrs=traffic_light,
            confirm=True,
        )
        print("create asset", json_dumps(asset, indent=4))
        self.assertEqual(
            asset["proof_mechanism"],
            ProofMechanism.SIMPLE_HASH.name,
            msg="Incorrect asset proof mechanism",
        )
        identity = asset["identity"]
        props = {
            "operation": "Record",
            "behaviour": "RecordEvidence",
        }

        # should cause at least 2 refreshes of token
        for i in range(25):
            sleep(60)
            event = new_arch.events.create(
                identity,
                props=props,
                attrs={
                    "arc_description": f"Safety conformance approved for version {i}",
                },
                confirm=True,
            )
            print(i, "create event", json_dumps(event, indent=4))
