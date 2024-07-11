"""
Test applications
"""

from copy import deepcopy
from json import dumps as json_dumps
from os import getenv
from time import sleep
from unittest import skipIf
from uuid import uuid4

from archivist import logger
from archivist.archivist import Archivist
from archivist.errors import ArchivistUnauthenticatedError
from archivist.utils import get_auth

from .constants import (
    PARTNER_ID_VALUE,
    USER_AGENT_VALUE,
    TestCase,
)

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

if getenv("DATATRAILS_LOGLEVEL") is not None:
    logger.set_logger(getenv("DATATRAILS_LOGLEVEL"))

LOGGER = logger.LOGGER


class TestApplications(TestCase):
    """
    Test Archivist Applications Create method
    """

    maxDiff = None

    def setUp(self):
        auth = get_auth(
            auth_token=getenv("DATATRAILS_AUTHTOKEN"),
            auth_token_filename=getenv("DATATRAILS_AUTHTOKEN_FILENAME"),
            client_id=getenv("DATATRAILS_APPREG_CLIENT"),
            client_secret=getenv("DATATRAILS_APPREG_SECRET"),
            client_secret_filename=getenv("DATATRAILS_APPREG_SECRET_FILENAME"),
        )
        self.arch = Archivist(
            getenv("DATATRAILS_URL"),
            auth,
            partner_id=PARTNER_ID_VALUE,
        )
        self.arch.user_agent = USER_AGENT_VALUE
        self.display_name = f"{DISPLAY_NAME} {uuid4()}"

    def tearDown(self):
        self.arch.close()

    def test_applications_create(self):
        """
        Test application creation
        """
        application = self.arch.applications.create(
            self.display_name,
            CUSTOM_CLAIMS,
        )
        LOGGER.debug("create application %s", json_dumps(application, indent=4))
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
        LOGGER.debug("create application %s", json_dumps(application, indent=4))
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
        LOGGER.debug("update application %s", json_dumps(application, indent=4))

    def test_applications_delete(self):
        """
        Test application delete
        """
        application = self.arch.applications.create(
            self.display_name,
            CUSTOM_CLAIMS,
        )
        LOGGER.debug("create application %s", json_dumps(application, indent=4))
        self.assertEqual(
            application["display_name"],
            self.display_name,
            msg="Incorrect display name",
        )
        application = self.arch.applications.delete(
            application["identity"],
        )
        LOGGER.debug("delete application %s", json_dumps(application, indent=4))
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
        LOGGER.debug("create application %s", json_dumps(application, indent=4))
        self.assertEqual(
            application["display_name"],
            self.display_name,
            msg="Incorrect display name",
        )
        application = self.arch.applications.regenerate(
            application["identity"],
        )
        LOGGER.debug("regenerate application %s", json_dumps(application, indent=4))

    def test_applications_list(self):
        """
        Test application list
        """
        application = self.arch.applications.create(
            self.display_name,
            CUSTOM_CLAIMS,
        )
        applications = list(self.arch.applications.list(display_name=self.display_name))
        self.assertGreater(
            len(applications),
            0,
            msg="Incorrect display name",
        )
        for application in applications:
            LOGGER.debug("application %s", json_dumps(application, indent=4))

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
        LOGGER.debug("create application %s", json_dumps(application, indent=4))
        self.assertEqual(
            application["display_name"],
            self.display_name,
            msg="Incorrect display name",
        )
        appidp = self.arch.appidp.token(
            application["client_id"],
            application["credentials"][0]["secret"],
        )
        LOGGER.debug("appidp %s", json_dumps(appidp, indent=4))

    def test_appidp_token_404(self):
        """
        Test appidp token
        """
        application = self.arch.applications.create(
            self.display_name,
            CUSTOM_CLAIMS,
        )
        client_id = application["client_id"]
        client_secret = "X" + application["credentials"][0]["secret"][1:]
        with self.assertRaises(ArchivistUnauthenticatedError):
            self.arch.appidp.token(
                client_id,
                client_secret,
            )

    @skipIf(
        getenv("DATATRAILS_REFRESH_TOKEN") is None,
        "cannot run test as DATATRAILS_REFRESH_TOKEN is not set",
    )
    def test_archivist_token(self):
        """
        Test archivist with client id/secret
        WARN: this test takes over 10 minutes
        """
        LOGGER.debug("This test takes over 10 minutes...")
        application = self.arch.applications.create(
            self.display_name,
            CUSTOM_CLAIMS,
        )
        LOGGER.debug("create application %s", json_dumps(application, indent=4))
        self.assertEqual(
            application["display_name"],
            self.display_name,
            msg="Incorrect display name",
        )

        # archivist using app registration
        LOGGER.debug("New Arch")
        with Archivist(
            getenv("DATATRAILS_URL"),
            (application["client_id"], application["credentials"][0]["secret"]),
        ) as new_arch:
            # now we create an asset and add events 10 times with a 60s sleep
            # this should trigger a token refresh
            traffic_light = deepcopy(ATTRS)
            traffic_light["arc_display_type"] = "Traffic light with violation camera"
            asset = new_arch.assets.create(
                attrs=traffic_light,
                confirm=True,
            )
            LOGGER.debug("create asset %s", json_dumps(asset, indent=4))
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
                LOGGER.debug("%d: create event %s", i, json_dumps(event, indent=4))
