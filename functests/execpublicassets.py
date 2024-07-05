"""
Test public assets creation
"""

from copy import deepcopy
from json import dumps as json_dumps
from os import getenv
from time import sleep

from archivist import logger
from archivist.archivist import Archivist
from archivist.constants import ASSET_BEHAVIOURS
from archivist.timestamp import now_timestamp
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
        "arc_display_name": ASSET_NAME,
        "arc_namespace": getenv("DATATRAILS_UNIQUE_ID"),
        "arc_firmware_version": "1.0",
        "arc_serial_number": "vtl-x4-07",
        "arc_description": "Traffic flow control light at A603 North East",
        "arc_display_type": "Traffic light with violation camera",
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
    "public": True,
}


class TestPublicAssetCreate(TestCase):
    """
    Test Archivist Public Asset Create method
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
        self.url = getenv("DATATRAILS_URL")
        self.arch = Archivist(
            getenv("DATATRAILS_URL"),
            auth,
            max_time=30,
            partner_id=PARTNER_ID_VALUE,
            user_agent=USER_AGENT_VALUE,
        )
        self.attrs = deepcopy(ATTRS)
        self.traffic_light = deepcopy(ATTRS)
        self.traffic_light["arc_display_type"] = "Traffic light with violation camera"

    def tearDown(self):
        self.arch.close()
        self.attrs = None
        self.traffic_light = None

    def test_public_asset_create(self):
        """
        Test public asset creation
        """
        asset = self.arch.assets.create(
            attrs=self.traffic_light,
            props={
                "public": True,
            },
            confirm=True,
        )
        LOGGER.debug("asset %s", json_dumps(asset, sort_keys=True, indent=4))
        self.assertEqual(
            asset["public"],
            True,
            msg="Asset is not public",
        )
        asset_publicurl = self.arch.assets.publicurl(asset["identity"])
        LOGGER.debug("asset_publicurl %s", asset_publicurl)
        public = self.arch.Public
        count = public.events.count(asset_id=asset_publicurl)
        LOGGER.debug("count %s", count)
        events = public.events.list(asset_id=asset_publicurl)
        LOGGER.debug("events %s", json_dumps(list(events), sort_keys=True, indent=4))

    def test_public_asset_create_event(self):
        """
        Test list
        """
        asset = self.arch.assets.create(
            attrs=self.traffic_light,
            props={
                "public": True,
            },
            confirm=True,
        )
        LOGGER.debug("asset %s", json_dumps(asset, sort_keys=True, indent=4))
        identity = asset["identity"]
        self.assertIsNotNone(
            identity,
            msg="Identity is None",
        )
        self.arch.assets.publicurl(asset["identity"])
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
        LOGGER.debug("event %s", json_dumps(event, sort_keys=True, indent=4))
        event_publicurl = self.arch.events.publicurl(event["identity"])

        public = self.arch.Public
        event = public.events.read(event_publicurl)
        LOGGER.debug("event %s", json_dumps(event, sort_keys=True, indent=4))

    def test_asset_create_if_not_exists_with_bad_attachment_assetattachment(self):
        """
        Test asset creation if not exists - check attachment for scanned status.

        Because we use create_if_not_exists the asset and attachments will persist.

        The test checks the scanned timestamp and checks scanned status.
        The first attachment should return OK after 24 hours and the second attachment
        should return bad after 24 hours.

        """
        request_data = deepcopy(REQUEST_EXISTS_ATTACHMENTS)
        request_data["attributes"]["arc_namespace"] = now_timestamp()
        LOGGER.debug("request_data %s", json_dumps(request_data, indent=4))
        asset, existed = self.arch.assets.create_if_not_exists(
            request_data,
            confirm=True,
        )
        LOGGER.debug("asset %s", json_dumps(asset, indent=4))
        LOGGER.debug("existed %s", existed)

        asset_id = asset["identity"]
        # first attachment is ok....
        attachment_id = asset["attributes"]["telephone"]["arc_blob_identity"]
        public_asset_id = self.arch.assets.publicurl(asset_id)
        LOGGER.debug("public asset id %s", public_asset_id)
        public = self.arch.Public
        sleep(30)  # until we implement confirmed logic
        info = public.assetattachments.info(public_asset_id, attachment_id)
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
        info = public.assetattachments.info(public_asset_id, attachment_id)
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
