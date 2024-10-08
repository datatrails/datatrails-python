"""
Test assets creation
"""

from copy import copy, deepcopy
from json import dumps as json_dumps
from os import getenv
from uuid import uuid4

from archivist import logger
from archivist.archivist import Archivist
from archivist.constants import ASSET_BEHAVIOURS
from archivist.proof_mechanism import ProofMechanism
from archivist.utils import get_auth

from .constants import (
    PARTNER_ID_VALUE,
    USER_AGENT_VALUE,
    TestCase,
)

# pylint: disable=fixme
# pylint: disable=missing-docstring
# pylint: disable=unused-variable


if getenv("DATATRAILS_LOGLEVEL") is not None:
    logger.set_logger(getenv("DATATRAILS_LOGLEVEL"))

LOGGER = logger.LOGGER


ATTRS = {
    "arc_firmware_version": "1.0",
    "arc_serial_number": "vtl-x4-07",
    "arc_description": "Traffic flow control light at A603 North East",
    "some_custom_attribute": "value",
}

MERKLE_LOG = {
    "proof_mechanism": ProofMechanism.MERKLE_LOG.name,
}

ASSET_NAME = "Telephone with 2 attachments - one bad or not scanned 2022-03-01"
REQUEST_EXISTS_ATTACHMENTS = {
    "selector": [
        {
            "attributes": [
                "arc_display_name",
                "arc_namespace",
            ]
        },
    ],
    "behaviours": ASSET_BEHAVIOURS,
    "attributes": {
        "arc_description": "Traffic flow control light at A603 North East",
        "arc_display_name": f"{ASSET_NAME}",
        "arc_display_type": "Traffic light with violation camera",
        "arc_firmware_version": "1.0",
        "arc_namespace": getenv("DATATRAILS_UNIQUE_ID"),
        "arc_serial_number": "vtl-x4-07",
        "some_custom_attribute": "value",
    },
    "attachments": [
        {
            "filename": "functests/test_resources/telephone.jpg",
            "content_type": "image/jpg",
            "attachment": "telephone",
        },
        {
            "url": "https://secure.eicar.org/eicarcom2.zip",
            "content_type": "application/zip",
            "attachment": "zipfile",
        },
    ],
}


class TestAssetCreate(TestCase):
    """
    Test Archivist Asset Create method
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
        self.attrs = deepcopy(ATTRS)
        self.traffic_light = deepcopy(ATTRS)
        self.traffic_light["arc_display_type"] = "Traffic light with violation camera"
        self.traffic_light_merkle_log = deepcopy(ATTRS)
        self.traffic_light_merkle_log["arc_display_type"] = (
            "Traffic light with violation camera (merkle_log)"
        )

    def tearDown(self):
        self.arch.close()
        self.arch = None
        self.attrs = None
        self.traffic_light = None

    def test_asset_create(self):
        """
        Test asset creation
        """
        asset = self.arch.assets.create(
            attrs=self.traffic_light,
            confirm=True,
        )
        LOGGER.debug("asset %s", json_dumps(asset, sort_keys=True, indent=4))
        tenancy = self.arch.tenancies.publicinfo(asset["tenant_identity"])
        LOGGER.debug("tenancy %s", json_dumps(tenancy, sort_keys=True, indent=4))

    def test_asset_create_merkle_log(self):
        """
        Test asset creation uses merkle_log proof mechanism
        """
        asset = self.arch.assets.create(
            props=MERKLE_LOG,
            attrs=self.traffic_light_merkle_log,
        )
        LOGGER.debug("asset %s", json_dumps(asset, sort_keys=True, indent=4))
        asset = self.arch.assets.wait_for_confirmation(asset["identity"])
        LOGGER.debug("asset %s", json_dumps(asset, sort_keys=True, indent=4))
        self.assertEqual(
            asset["proof_mechanism"],
            ProofMechanism.MERKLE_LOG.name,
            msg="Incorrect asset proof mechanism",
        )
        tenancy = self.arch.tenancies.publicinfo(asset["tenant_identity"])
        LOGGER.debug("tenancy %s", json_dumps(tenancy, sort_keys=True, indent=4))

    def test_asset_create_with_fixtures(self):
        """
        Test creation with fixtures
        """
        # create traffic lights endpoint
        traffic_lights = copy(self.arch)
        traffic_lights.fixtures = {
            "assets": {
                "attributes": {
                    "arc_display_type": "Traffic light with violation camera",
                    "arc_namespace": f"functests {uuid4()}",
                },
            },
        }
        traffic_lights.assets.create(
            attrs=self.attrs,
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
        fancy_traffic_lights.assets.create(
            attrs=self.attrs,
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
        asset, existed = self.arch.assets.create_if_not_exists(
            REQUEST_EXISTS_ATTACHMENTS,
        )
        identity = asset["identity"]

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
            identity,
            props=props,
            attrs=attrs,
        )
        LOGGER.debug("event %s", json_dumps(event, sort_keys=True, indent=4))

        # must wait for tenant_identity to be populated
        event = self.arch.events.wait_for_confirmation(event["identity"])
        LOGGER.debug("event %s", json_dumps(event, sort_keys=True, indent=4))

        tenancy = self.arch.tenancies.publicinfo(event["tenant_identity"])
        LOGGER.debug("tenancy %s", json_dumps(tenancy, sort_keys=True, indent=4))


class TestAssetCreateIfNotExists(TestCase):
    """
    Test Archivist Asset CreateIfNotExists method
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

    def tearDown(self):
        self.arch.close()
        self.arch = None

    def test_asset_create_if_not_exists_with_bad_attachment(self):
        """
        Test asset creation if not exists - check attachment for scanned status.

        Because we use create_if_not_exists the asset and attachments will persist.

        The test checks the scanned timestamp and checks scanned status.
        The first attachment should return OK after 24 hours and the second attachment
        should return bad after 24 hours.

        """
        asset, existed = self.arch.assets.create_if_not_exists(
            REQUEST_EXISTS_ATTACHMENTS,
        )
        LOGGER.debug("asset %s", json_dumps(asset, indent=4))
        LOGGER.debug("existed %s", existed)

        # first attachment is ok....
        attachment_id = asset["attributes"]["telephone"]["arc_blob_identity"]
        info = self.arch.attachments.info(
            attachment_id,
        )
        LOGGER.debug("info attachment1 %s", json_dumps(info, indent=4))
        timestamp = info["scanned_timestamp"]
        if timestamp:
            LOGGER.debug("%d: scanned last at %s", attachment_id, timestamp)
            LOGGER.debug("%d: scanned status %s", attachment_id, info["scanned_status"])
            LOGGER.debug("%d: scanned reason %s", attachment_id, info["scanned_reason"])
            self.assertEqual(
                info["scanned_status"],
                "SCANNED_OK",
                msg="First attachment is not clean",
            )

        # second attachment is bad when scanned....
        attachment_id = asset["attributes"]["zipfile"]["arc_blob_identity"]
        info = self.arch.attachments.info(
            attachment_id,
        )
        LOGGER.debug("info attachment1 %s", json_dumps(info, indent=4))
        timestamp = info["scanned_timestamp"]
        if timestamp:
            LOGGER.debug("%d: scanned last at %s", attachment_id, timestamp)
            LOGGER.debug("%d: scanned status %s", attachment_id, info["scanned_status"])
            LOGGER.debug("%d: scanned reason %s", attachment_id, info["scanned_reason"])
            self.assertEqual(
                info["scanned_status"],
                "SCANNED_BAD",
                msg="First attachment should not be clean",
            )

    def test_asset_create_if_not_exists_with_bad_attachment_assetattachment(self):
        """
        Test asset creation if not exists - check attachment for scanned status.

        Because we use create_if_not_exists the asset and attachments will persist.

        The test checks the scanned timestamp and checks scanned status.
        The first attachment should return OK after 24 hours and the second attachment
        should return bad after 24 hours.

        """
        asset, existed = self.arch.assets.create_if_not_exists(
            REQUEST_EXISTS_ATTACHMENTS,
        )
        LOGGER.debug("asset %s", json_dumps(asset, indent=4))
        LOGGER.debug("existed %s", existed)

        # first attachment is ok....
        attachment_id = asset["attributes"]["telephone"]["arc_blob_identity"]
        info = self.arch.assetattachments.info(
            asset["identity"],
            attachment_id,
        )
        LOGGER.debug("info attachment1 %s", json_dumps(info, indent=4))
        timestamp = info["scanned_timestamp"]
        if timestamp:
            LOGGER.debug("%d: scanned last at %s", attachment_id, timestamp)
            LOGGER.debug("%d: scanned status %s", attachment_id, info["scanned_status"])
            LOGGER.debug("%d: scanned reason %s", attachment_id, info["scanned_reason"])
            self.assertEqual(
                info["scanned_status"],
                "SCANNED_OK",
                msg="First attachment is not clean",
            )

        # second attachment is bad when scanned....
        attachment_id = asset["attributes"]["zipfile"]["arc_blob_identity"]
        info = self.arch.assetattachments.info(
            asset["identity"],
            attachment_id,
        )
        LOGGER.debug("info attachment1 %s", json_dumps(info, indent=4))
        timestamp = info["scanned_timestamp"]
        if timestamp:
            LOGGER.debug("%d: scanned last at %s", attachment_id, timestamp)
            LOGGER.debug("%d: scanned status %s", attachment_id, info["scanned_status"])
            LOGGER.debug("%d: scanned reason %s", attachment_id, info["scanned_reason"])
            self.assertEqual(
                info["scanned_status"],
                "SCANNED_BAD",
                msg="First attachment should not be clean",
            )
