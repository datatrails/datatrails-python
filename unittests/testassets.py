"""
Test archivist
"""

import json

from unittest import TestCase, mock

from archivist.archivist import Archivist
from archivist.assets import DEFAULT_PAGE_SIZE
from archivist import confirm
from archivist.constants import (
    ASSETS_LABEL,
    ASSETS_SUBPATH,
    HEADERS_REQUEST_TOTAL_COUNT,
    HEADERS_TOTAL_COUNT,
    ROOT,
)
from archivist.errors import ArchivistUnconfirmedError

from .mock_response import MockResponse

# pylint: disable=missing-docstring
# pylint: disable=unused-variable


BEHAVIOURS = [
    "Firmware",
    "Maintenance",
    "RecordEvidence",
    "LocationUpdate",
    "Attachments",
]
PRIMARY_IMAGE = {
    "arc_display_name": "arc_primary_image",
    "arc_attachment_identity": "blobs/87b1a84c-1c6f-442b-923e-a97516f4d275",
    "arc_hash_alg": "SHA256",
    "arc_hash_value": "246c316e2cd6971ce5c83a3e61f9880fa6e2f14ae2976ee03500eb282fd03a60",
}
SECONDARY_IMAGE = {
    "arc_display_name": "arc_secondary_image",
    "arc_attachment_identity": "blobs/87b1a84c-1c6f-442b-923e-a97516f4d275",
    "arc_hash_alg": "SHA256",
    "arc_hash_value": "246c316e2cd6971ce5c83a3e61f9880fa6e2f14ae2976ee03500eb282fd03a60",
}
TERTIARY_IMAGE = {
    "arc_attachment_identity": "blobs/87b1a84c-1c6f-442b-923e-a97516f4d275",
    "arc_hash_alg": "SHA256",
    "arc_hash_value": "246c316e2cd6971ce5c83a3e61f9880fa6e2f14ae2976ee03500eb282fd03a60",
}
ASSET_NAME = "tcl.ppj.003"
BASE_ATTRS = {
    "arc_firmware_version": "1.0",
    "arc_serial_number": "vtl-x4-07",
    "arc_description": "Traffic flow control light at A603 North East",
    "arc_home_location_identity": "locations/115340cf-f39e-4d43-a2ee-8017d672c6c6",
    "arc_display_type": "Traffic light with violation camera",
    "some_custom_attribute": "value",
}
ATTRS_WITH_NAME = {
    **BASE_ATTRS,
    "arc_display_name": ASSET_NAME,
}

ATTRS = {
    **ATTRS_WITH_NAME,
    "arc_attachments": [
        TERTIARY_IMAGE,
        SECONDARY_IMAGE,
        PRIMARY_IMAGE,
    ],
}
# also has no arc_display_name
ATTRS_NO_ATTACHMENTS = {
    **BASE_ATTRS,
}

IDENTITY = f"{ASSETS_LABEL}/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
SUBPATH = f"{ASSETS_SUBPATH}/{ASSETS_LABEL}"

# TBD: add properties as well
REQUEST = {
    "behaviours": BEHAVIOURS,
    "attributes": ATTRS,
}
REQUEST_DATA = json.dumps(REQUEST)

RESPONSE = {
    "identity": IDENTITY,
    "behaviours": BEHAVIOURS,
    "attributes": ATTRS,
    "confirmation_status": "CONFIRMED",
}

RESPONSE_NO_ATTACHMENTS = {
    "identity": IDENTITY,
    "behaviours": BEHAVIOURS,
    "attributes": ATTRS_NO_ATTACHMENTS,
    "confirmation_status": "CONFIRMED",
}
RESPONSE_NO_CONFIRMATION = {
    "identity": IDENTITY,
    "behaviours": BEHAVIOURS,
    "attributes": ATTRS,
}
RESPONSE_PENDING = {
    "identity": IDENTITY,
    "behaviours": BEHAVIOURS,
    "attributes": ATTRS,
    "confirmation_status": "PENDING",
}
RESPONSE_FAILED = {
    "identity": IDENTITY,
    "behaviours": BEHAVIOURS,
    "attributes": ATTRS,
    "confirmation_status": "FAILED",
}


class TestAssets(TestCase):
    """
    Test Archivist Assets Create method
    """

    maxDiff = None

    def setUp(self):
        self.arch = Archivist("url", auth="authauthauth")
        self.confirm_MAX_TIME = confirm.MAX_TIME
        confirm.MAX_TIME = 2

    def tearDown(self):
        confirm.MAX_TIME = self.confirm_MAX_TIME

    @mock.patch("requests.post")
    def test_assets_create(self, mock_post):
        """
        Test asset creation
        """
        mock_post.return_value = MockResponse(200, **RESPONSE)

        asset = self.arch.assets.create(BEHAVIOURS, ATTRS, confirm=False)
        self.assertEqual(
            tuple(mock_post.call_args),
            (
                ((f"url/{ROOT}/{ASSETS_SUBPATH}" f"/{ASSETS_LABEL}"),),
                {
                    "data": REQUEST_DATA,
                    "headers": {
                        "content-type": "application/json",
                        "authorization": "Bearer authauthauth",
                    },
                    "verify": True,
                    "cert": None,
                },
            ),
            msg="CREATE method called incorrectly",
        )
        self.assertEqual(
            asset,
            RESPONSE,
            msg="CREATE method called incorrectly",
        )
        self.assertEqual(
            asset.primary_image,
            PRIMARY_IMAGE,
            msg="Incorrect primary image",
        )
        self.assertEqual(
            asset.name,
            ASSET_NAME,
            msg="Incorrect name property",
        )

    @mock.patch("requests.get")
    @mock.patch("requests.post")
    def test_assets_create_with_confirmation(self, mock_post, mock_get):
        """
        Test asset creation
        """
        mock_post.return_value = MockResponse(200, **RESPONSE)
        mock_get.return_value = MockResponse(200, **RESPONSE)
        asset = self.arch.assets.create(BEHAVIOURS, ATTRS, confirm=True)
        self.assertEqual(
            asset,
            RESPONSE,
            msg="CREATE method called incorrectly",
        )

    @mock.patch("requests.get")
    @mock.patch("requests.post")
    def test_assets_create_with_confirmation_no_confirmed_status(
        self,
        mock_post,
        mock_get,
    ):
        """
        Test asset confirmation
        """
        mock_post.return_value = MockResponse(200, **RESPONSE)
        mock_get.return_value = MockResponse(200, **RESPONSE_NO_CONFIRMATION)

        with self.assertRaises(ArchivistUnconfirmedError):
            asset = self.arch.assets.create(BEHAVIOURS, ATTRS, confirm=True)

    @mock.patch("requests.get")
    @mock.patch("requests.post")
    def test_assets_create_with_confirmation_pending_status(
        self,
        mock_post,
        mock_get,
    ):
        """
        Test asset confirmation
        """
        mock_post.return_value = MockResponse(200, **RESPONSE)
        mock_get.side_effect = [
            MockResponse(200, **RESPONSE_PENDING),
            MockResponse(200, **RESPONSE),
        ]
        asset = self.arch.assets.create(BEHAVIOURS, ATTRS, confirm=True)
        self.assertEqual(
            asset,
            RESPONSE,
            msg="CREATE method called incorrectly",
        )

    @mock.patch("requests.get")
    @mock.patch("requests.post")
    def test_assets_create_with_confirmation_failed_status(
        self,
        mock_post,
        mock_get,
    ):
        """
        Test asset confirmation
        """
        mock_post.return_value = MockResponse(200, **RESPONSE)
        mock_get.side_effect = [
            MockResponse(200, **RESPONSE_PENDING),
            MockResponse(200, **RESPONSE_FAILED),
        ]
        with self.assertRaises(ArchivistUnconfirmedError):
            asset = self.arch.assets.create(BEHAVIOURS, ATTRS, confirm=True)

    @mock.patch("requests.get")
    @mock.patch("requests.post")
    def test_assets_create_with_confirmation_always_pending_status(
        self,
        mock_post,
        mock_get,
    ):
        """
        Test asset confirmation
        """
        mock_post.return_value = MockResponse(200, **RESPONSE)
        mock_get.side_effect = [
            MockResponse(200, **RESPONSE_PENDING),
            MockResponse(200, **RESPONSE_PENDING),
            MockResponse(200, **RESPONSE_PENDING),
            MockResponse(200, **RESPONSE_PENDING),
            MockResponse(200, **RESPONSE_PENDING),
            MockResponse(200, **RESPONSE_PENDING),
            MockResponse(200, **RESPONSE_PENDING),
        ]
        with self.assertRaises(ArchivistUnconfirmedError):
            asset = self.arch.assets.create(BEHAVIOURS, ATTRS, confirm=True)

    @mock.patch("requests.get")
    def test_assets_read_with_out_primary_image(self, mock_get):
        """
        Test asset reading
        """
        mock_get.return_value = MockResponse(200, **RESPONSE_NO_ATTACHMENTS)

        asset = self.arch.assets.read(IDENTITY)
        self.assertEqual(
            asset,
            RESPONSE_NO_ATTACHMENTS,
            msg="READ method called incorrectly",
        )
        self.assertIsNone(
            asset.primary_image,
            msg="There should be no primary image",
        )
        self.assertIsNone(
            asset.name,
            msg="There should be no name property",
        )

    @mock.patch("requests.get")
    def test_assets_count(self, mock_get):
        """
        Test asset counting
        """
        mock_get.return_value = MockResponse(
            200,
            headers={HEADERS_TOTAL_COUNT: 1},
            assets=[
                RESPONSE,
            ],
        )

        count = self.arch.assets.count()
        self.assertEqual(
            count,
            1,
            msg="Incorrect count",
        )
        self.assertEqual(
            tuple(mock_get.call_args),
            (
                ((f"url/{ROOT}/{SUBPATH}" "?page_size=1"),),
                {
                    "headers": {
                        "content-type": "application/json",
                        "authorization": "Bearer authauthauth",
                        HEADERS_REQUEST_TOTAL_COUNT: "true",
                    },
                    "verify": True,
                    "cert": None,
                },
            ),
            msg="GET method called incorrectly",
        )

    @mock.patch("requests.get")
    def test_assets_count_with_props_query(self, mock_get):
        """
        Test asset counting
        """
        mock_get.return_value = MockResponse(
            200,
            headers={HEADERS_TOTAL_COUNT: 1},
            assets=[
                RESPONSE,
            ],
        )

        count = self.arch.assets.count(
            props={
                "confirmation_status": "CONFIRMED",
            },
        )
        self.assertEqual(
            tuple(mock_get.call_args),
            (
                (
                    (
                        f"url/{ROOT}/{SUBPATH}"
                        "?page_size=1"
                        "&confirmation_status=CONFIRMED"
                    ),
                ),
                {
                    "headers": {
                        "content-type": "application/json",
                        "authorization": "Bearer authauthauth",
                        HEADERS_REQUEST_TOTAL_COUNT: "true",
                    },
                    "verify": True,
                    "cert": None,
                },
            ),
            msg="GET method called incorrectly",
        )

    @mock.patch("requests.get")
    def test_assets_count_with_attrs_query(self, mock_get):
        """
        Test asset counting
        """
        mock_get.return_value = MockResponse(
            200,
            headers={HEADERS_TOTAL_COUNT: 1},
            assets=[
                RESPONSE,
            ],
        )

        count = self.arch.assets.count(
            attrs={"arc_firmware_version": "1.0"},
        )
        self.assertEqual(
            tuple(mock_get.call_args),
            (
                (
                    (
                        f"url/{ROOT}/{SUBPATH}"
                        "?page_size=1"
                        "&attributes.arc_firmware_version=1.0"
                    ),
                ),
                {
                    "headers": {
                        "content-type": "application/json",
                        "authorization": "Bearer authauthauth",
                        HEADERS_REQUEST_TOTAL_COUNT: "true",
                    },
                    "verify": True,
                    "cert": None,
                },
            ),
            msg="GET method called incorrectly",
        )

    @mock.patch("requests.get")
    def test_assets_wait_for_confirmed(self, mock_get):
        """
        Test asset counting
        """
        ## last call to get looks for FAILED assets
        status = ("PENDING", "PENDING", "FAILED")
        mock_get.side_effect = [
            MockResponse(
                200,
                headers={HEADERS_TOTAL_COUNT: 2},
                assets=[
                    RESPONSE_PENDING,
                ],
            ),
            MockResponse(
                200,
                headers={HEADERS_TOTAL_COUNT: 0},
                assets=[],
            ),
            MockResponse(
                200,
                headers={HEADERS_TOTAL_COUNT: 0},
                assets=[],
            ),
        ]

        self.arch.assets.wait_for_confirmed()
        for i, a in enumerate(mock_get.call_args_list):
            self.assertEqual(
                tuple(a),
                (
                    (
                        (
                            f"url/{ROOT}/{SUBPATH}"
                            "?page_size=1"
                            f"&confirmation_status={status[i]}"
                        ),
                    ),
                    {
                        "headers": {
                            "content-type": "application/json",
                            "authorization": "Bearer authauthauth",
                            HEADERS_REQUEST_TOTAL_COUNT: "true",
                        },
                        "verify": True,
                        "cert": None,
                    },
                ),
                msg="GET method called incorrectly",
            )

    @mock.patch("requests.get")
    def test_assets_wait_for_confirmed_timeout(self, mock_get):
        """
        Test asset counting
        """
        ## last call to get looks for FAILED assets
        mock_get.side_effect = [
            MockResponse(
                200,
                headers={HEADERS_TOTAL_COUNT: 2},
                assets=[
                    RESPONSE_PENDING,
                ],
            ),
            MockResponse(
                200,
                headers={HEADERS_TOTAL_COUNT: 2},
                assets=[
                    RESPONSE_PENDING,
                ],
            ),
            MockResponse(
                200,
                headers={HEADERS_TOTAL_COUNT: 2},
                assets=[
                    RESPONSE_PENDING,
                ],
            ),
            MockResponse(
                200,
                headers={HEADERS_TOTAL_COUNT: 2},
                assets=[
                    RESPONSE_PENDING,
                ],
            ),
            MockResponse(
                200,
                headers={HEADERS_TOTAL_COUNT: 2},
                assets=[
                    RESPONSE_PENDING,
                ],
            ),
            MockResponse(
                200,
                headers={HEADERS_TOTAL_COUNT: 2},
                assets=[
                    RESPONSE_PENDING,
                ],
            ),
        ]

        self.arch.assets.timeout = 2
        with self.assertRaises(ArchivistUnconfirmedError):
            self.arch.assets.wait_for_confirmed()

    @mock.patch("requests.get")
    def test_assets_wait_for_confirmed_failed(self, mock_get):
        """
        Test asset counting
        """
        ## last call to get looks for FAILED assets
        mock_get.side_effect = [
            MockResponse(
                200,
                headers={HEADERS_TOTAL_COUNT: 2},
                assets=[
                    RESPONSE_PENDING,
                ],
            ),
            MockResponse(
                200,
                headers={HEADERS_TOTAL_COUNT: 0},
                assets=[],
            ),
            MockResponse(
                200,
                headers={HEADERS_TOTAL_COUNT: 1},
                assets=[
                    RESPONSE_FAILED,
                ],
            ),
        ]

        with self.assertRaises(ArchivistUnconfirmedError):
            self.arch.assets.wait_for_confirmed()

    @mock.patch("requests.get")
    def test_assets_list(self, mock_get):
        """
        Test asset listing
        """
        mock_get.return_value = MockResponse(
            200,
            assets=[
                RESPONSE,
            ],
        )

        assets = list(self.arch.assets.list())
        self.assertEqual(
            len(assets),
            1,
            msg="incorrect number of assets",
        )
        for asset in assets:
            self.assertEqual(
                asset,
                RESPONSE,
                msg="Incorrect asset listed",
            )

        for a in mock_get.call_args_list:
            self.assertEqual(
                tuple(a),
                (
                    (f"url/{ROOT}/{SUBPATH}?page_size={DEFAULT_PAGE_SIZE}",),
                    {
                        "headers": {
                            "content-type": "application/json",
                            "authorization": "Bearer authauthauth",
                        },
                        "verify": True,
                        "cert": None,
                    },
                ),
                msg="GET method called incorrectly",
            )

    @mock.patch("requests.get")
    def test_assets_list_with_query(self, mock_get):
        """
        Test asset listing
        """
        mock_get.return_value = MockResponse(
            200,
            assets=[
                RESPONSE,
            ],
        )

        assets = list(
            self.arch.assets.list(
                props={
                    "confirmation_status": "CONFIRMED",
                },
                attrs={"arc_firmware_version": "1.0"},
            )
        )
        self.assertEqual(
            len(assets),
            1,
            msg="incorrect number of assets",
        )
        for asset in assets:
            self.assertEqual(
                asset,
                RESPONSE,
                msg="Incorrect asset listed",
            )

        for a in mock_get.call_args_list:
            self.assertEqual(
                tuple(a),
                (
                    (
                        (
                            f"url/{ROOT}/{SUBPATH}"
                            f"?page_size={DEFAULT_PAGE_SIZE}"
                            "&attributes.arc_firmware_version=1.0"
                            "&confirmation_status=CONFIRMED"
                        ),
                    ),
                    {
                        "headers": {
                            "content-type": "application/json",
                            "authorization": "Bearer authauthauth",
                        },
                        "verify": True,
                        "cert": None,
                    },
                ),
                msg="GET method called incorrectly",
            )

    @mock.patch("requests.get")
    def test_assets_read_by_signature(self, mock_get):
        """
        Test asset listing
        """
        mock_get.return_value = MockResponse(
            200,
            assets=[
                RESPONSE,
            ],
        )

        asset = self.arch.assets.read_by_signature()
        self.assertEqual(
            asset,
            RESPONSE,
            msg="Incorrect asset listed",
        )

        self.assertEqual(
            tuple(mock_get.call_args),
            (
                (f"url/{ROOT}/{SUBPATH}?page_size=2",),
                {
                    "headers": {
                        "content-type": "application/json",
                        "authorization": "Bearer authauthauth",
                    },
                    "verify": True,
                    "cert": None,
                },
            ),
            msg="GET method called incorrectly",
        )
