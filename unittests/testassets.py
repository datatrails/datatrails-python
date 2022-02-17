"""
Test archivist
"""

from copy import copy
from logging import getLogger
from os import environ

from unittest import TestCase, mock

from archivist.archivist import Archivist
from archivist.assets import BEHAVIOURS
from archivist.constants import (
    ASSETS_LABEL,
    ASSETS_SUBPATH,
    HEADERS_REQUEST_TOTAL_COUNT,
    HEADERS_TOTAL_COUNT,
    ROOT,
)
from archivist.errors import ArchivistNotFoundError, ArchivistUnconfirmedError
from archivist.logger import set_logger
from archivist.proof_mechanism import ProofMechanism

from .mock_response import MockResponse

# pylint: disable=missing-docstring
# pylint: disable=protected-access
# pylint: disable=unused-variable

if "TEST_DEBUG" in environ and environ["TEST_DEBUG"]:
    set_logger(environ["TEST_DEBUG"])

LOGGER = getLogger(__name__)

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

PROPS = {
    "proof_mechanism": ProofMechanism.SIMPLE_HASH.name,
}
FIXTURES_ATTRIBUTES = {
    "arc_namespace": "namespace",
}
FIXTURES = {
    "assets": {
        "attributes": FIXTURES_ATTRIBUTES,
    },
}
ATTRS_FIXTURES = {**FIXTURES_ATTRIBUTES, **ATTRS}

REQUEST = {
    "behaviours": BEHAVIOURS,
    "proof_mechanism": ProofMechanism.SIMPLE_HASH.name,
    "attributes": ATTRS,
}
REQUEST_KWARGS = {
    "json": REQUEST,
    "headers": {
        "authorization": "Bearer authauthauth",
    },
    "verify": True,
}

REQUEST_FIXTURES = {
    "behaviours": BEHAVIOURS,
    "proof_mechanism": ProofMechanism.SIMPLE_HASH.name,
    "attributes": ATTRS_FIXTURES,
}
REQUEST_FIXTURES_KWARGS = {
    "json": REQUEST_FIXTURES,
    "headers": {
        "authorization": "Bearer authauthauth",
    },
    "verify": True,
}

RESPONSE = {
    "identity": IDENTITY,
    "behaviours": BEHAVIOURS,
    "attributes": ATTRS,
    "confirmation_status": "CONFIRMED",
}
RESPONSE_FIXTURES = {
    "identity": IDENTITY,
    "behaviours": BEHAVIOURS,
    "attributes": ATTRS_FIXTURES,
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


class TestAssetsBase(TestCase):
    """
    Test Archivist Assets Base
    """

    maxDiff = None

    def setUp(self):
        self.arch = Archivist("url", "authauthauth", max_time=1)

    def tearDown(self):
        self.arch = None


class TestAssetsUtil(TestAssetsBase):
    """
    Test Archivist Assets utility
    """

    def test_assets_str(self):
        """
        Test assets str
        """
        self.assertEqual(
            str(self.arch.assets),
            "AssetsClient(url)",
            msg="Incorrect str",
        )


class TestAssetsCreate(TestAssetsBase):
    """
    Test Archivist Assets methods
    """

    def test_assets_create(self):
        """
        Test asset creation
        """
        with mock.patch.object(self.arch._session, "post", autospec=True) as mock_post:
            mock_post.return_value = MockResponse(200, **RESPONSE)

            asset = self.arch.assets.create(props=PROPS, attrs=ATTRS, confirm=False)
            args, kwargs = mock_post.call_args
            self.assertEqual(
                args,
                (f"url/{ROOT}/{ASSETS_SUBPATH}/{ASSETS_LABEL}",),
                msg="CREATE method args called incorrectly",
            )
            self.assertEqual(
                kwargs,
                REQUEST_KWARGS,
                msg="CREATE method kwargs called incorrectly",
            )
            self.assertEqual(
                asset,
                RESPONSE,
                msg="CREATE incorrect response",
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

    def test_assets_create_with_fixtures(self):
        """
        Test asset creation
        """
        arch = copy(self.arch)
        arch.fixtures = FIXTURES
        with mock.patch.object(arch._session, "post", autospec=True) as mock_post:
            mock_post.return_value = MockResponse(200, **RESPONSE_FIXTURES)
            asset = arch.assets.create(props=PROPS, attrs=ATTRS, confirm=False)
            args, kwargs = mock_post.call_args
            self.assertEqual(
                args,
                (f"url/{ROOT}/{ASSETS_SUBPATH}/{ASSETS_LABEL}",),
                msg="CREATE method args called incorrectly",
            )
            self.assertEqual(
                kwargs,
                REQUEST_FIXTURES_KWARGS,
                msg="CREATE method kwargs called incorrectly",
            )
            self.assertEqual(
                asset,
                RESPONSE_FIXTURES,
                msg="CREATE method called incorrectly",
            )

    def test_assets_create_with_confirmation(self):
        """
        Test asset creation
        """
        with mock.patch.object(
            self.arch._session, "post"
        ) as mock_post, mock.patch.object(self.arch._session, "get") as mock_get:
            mock_post.return_value = MockResponse(200, **RESPONSE)
            mock_get.return_value = MockResponse(200, **RESPONSE)
            asset = self.arch.assets.create(props=PROPS, attrs=ATTRS, confirm=True)
            self.assertEqual(
                asset,
                RESPONSE,
                msg="CREATE method called incorrectly",
            )

    def test_assets_create_with_explicit_confirmation(self):
        """
        Test asset creation
        """
        with mock.patch.object(
            self.arch._session, "post"
        ) as mock_post, mock.patch.object(self.arch._session, "get") as mock_get:
            mock_post.return_value = MockResponse(200, **RESPONSE)
            mock_get.return_value = MockResponse(200, **RESPONSE)
            asset = self.arch.assets.create(props=PROPS, attrs=ATTRS, confirm=False)
            self.arch.assets.wait_for_confirmation(asset["identity"])
            self.assertEqual(
                asset,
                RESPONSE,
                msg="CREATE method called incorrectly",
            )

    def test_assets_create_with_confirmation_no_confirmed_status(self):
        """
        Test asset confirmation
        """
        with mock.patch.object(
            self.arch._session, "post"
        ) as mock_post, mock.patch.object(self.arch._session, "get") as mock_get:
            mock_post.return_value = MockResponse(200, **RESPONSE)
            mock_get.return_value = MockResponse(200, **RESPONSE_NO_CONFIRMATION)

            with self.assertRaises(ArchivistUnconfirmedError):
                asset = self.arch.assets.create(props=PROPS, attrs=ATTRS, confirm=True)

    def test_assets_create_with_confirmation_pending_status(self):
        """
        Test asset confirmation
        """
        with mock.patch.object(
            self.arch._session, "post"
        ) as mock_post, mock.patch.object(self.arch._session, "get") as mock_get:
            mock_post.return_value = MockResponse(200, **RESPONSE)
            mock_get.side_effect = [
                MockResponse(200, **RESPONSE_PENDING),
                MockResponse(200, **RESPONSE),
            ]
            asset = self.arch.assets.create(props=PROPS, attrs=ATTRS, confirm=True)
            self.assertEqual(
                asset,
                RESPONSE,
                msg="CREATE method called incorrectly",
            )

    def test_assets_create_with_confirmation_failed_status(self):
        """
        Test asset confirmation
        """
        with mock.patch.object(
            self.arch._session, "post"
        ) as mock_post, mock.patch.object(self.arch._session, "get") as mock_get:
            mock_post.return_value = MockResponse(200, **RESPONSE)
            mock_get.side_effect = [
                MockResponse(200, **RESPONSE_PENDING),
                MockResponse(200, **RESPONSE_FAILED),
            ]
            with self.assertRaises(ArchivistUnconfirmedError):
                asset = self.arch.assets.create(props=PROPS, attrs=ATTRS, confirm=True)

    def test_assets_create_with_confirmation_always_pending_status(self):
        """
        Test asset confirmation
        """
        with mock.patch.object(
            self.arch._session, "post"
        ) as mock_post, mock.patch.object(self.arch._session, "get") as mock_get:
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
                asset = self.arch.assets.create(props=PROPS, attrs=ATTRS, confirm=True)


class TestAssetsRead(TestAssetsBase):
    """
    Test Archivist Assets methods
    """

    def test_assets_read_with_out_primary_image(self):
        """
        Test asset reading
        """
        with mock.patch.object(self.arch._session, "get") as mock_get:
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


class TestAssetsCount(TestAssetsBase):
    """
    Test Archivist Assets methods
    """

    def test_assets_count(self):
        """
        Test asset counting
        """
        with mock.patch.object(self.arch._session, "get") as mock_get:
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
                    ((f"url/{ROOT}/{SUBPATH}"),),
                    {
                        "headers": {
                            "authorization": "Bearer authauthauth",
                            HEADERS_REQUEST_TOTAL_COUNT: "true",
                        },
                        "params": {"page_size": 1},
                        "verify": True,
                    },
                ),
                msg="GET method called incorrectly",
            )

    def test_assets_count_with_props_params(self):
        """
        Test asset counting
        """
        with mock.patch.object(self.arch._session, "get") as mock_get:
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
                    ((f"url/{ROOT}/{SUBPATH}"),),
                    {
                        "headers": {
                            "authorization": "Bearer authauthauth",
                            HEADERS_REQUEST_TOTAL_COUNT: "true",
                        },
                        "params": {
                            "page_size": 1,
                            "confirmation_status": "CONFIRMED",
                        },
                        "verify": True,
                    },
                ),
                msg="GET method called incorrectly",
            )

    def test_assets_count_with_attrs_params(self):
        """
        Test asset counting
        """
        with mock.patch.object(self.arch._session, "get") as mock_get:
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
                    ((f"url/{ROOT}/{SUBPATH}"),),
                    {
                        "headers": {
                            "authorization": "Bearer authauthauth",
                            HEADERS_REQUEST_TOTAL_COUNT: "true",
                        },
                        "params": {
                            "page_size": 1,
                            "attributes.arc_firmware_version": "1.0",
                        },
                        "verify": True,
                    },
                ),
                msg="GET method called incorrectly",
            )


class TestAssetsWait(TestAssetsBase):
    """
    Test Archivist Assets methods
    """

    def test_assets_wait_for_confirmed(self):
        """
        Test asset counting
        """
        ## last call to get looks for FAILED assets
        status = (
            {"page_size": 1},
            {"page_size": 1, "confirmation_status": "PENDING"},
            {"page_size": 1, "confirmation_status": "FAILED"},
        )
        with mock.patch.object(self.arch._session, "get") as mock_get:
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
                        (f"url/{ROOT}/{SUBPATH}",),
                        {
                            "headers": {
                                "authorization": "Bearer authauthauth",
                                HEADERS_REQUEST_TOTAL_COUNT: "true",
                            },
                            "params": status[i],
                            "verify": True,
                        },
                    ),
                    msg="GET method called incorrectly",
                )

    def test_assets_wait_for_confirmed_not_found(self):
        """
        Test asset counting
        """
        with mock.patch.object(self.arch._session, "get") as mock_get:
            mock_get.side_effect = [
                MockResponse(
                    200,
                    headers={HEADERS_TOTAL_COUNT: 0},
                    assets=[
                        RESPONSE_PENDING,
                    ],
                ),
            ]

            with self.assertRaises(ArchivistNotFoundError):
                self.arch.assets.wait_for_confirmed()

    def test_assets_wait_for_confirmed_timeout(self):
        """
        Test asset counting
        """
        ## last call to get looks for FAILED assets
        with mock.patch.object(self.arch._session, "get") as mock_get:
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

            with self.assertRaises(ArchivistUnconfirmedError):
                self.arch.assets.wait_for_confirmed()

    def test_assets_wait_for_confirmed_failed(self):
        """
        Test asset counting
        """
        ## last call to get looks for FAILED assets
        with mock.patch.object(self.arch._session, "get") as mock_get:
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


class TestAssetsList(TestAssetsBase):
    """
    Test Archivist Assets methods
    """

    def test_assets_list(self):
        """
        Test asset listing
        """
        with mock.patch.object(self.arch._session, "get") as mock_get:
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
                        (f"url/{ROOT}/{SUBPATH}",),
                        {
                            "headers": {
                                "authorization": "Bearer authauthauth",
                            },
                            "params": {},
                            "verify": True,
                        },
                    ),
                    msg="GET method called incorrectly",
                )

    def test_assets_list_with_params(self):
        """
        Test asset listing
        """
        with mock.patch.object(self.arch._session, "get") as mock_get:
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
                        ((f"url/{ROOT}/{SUBPATH}"),),
                        {
                            "headers": {
                                "authorization": "Bearer authauthauth",
                            },
                            "params": {
                                "confirmation_status": "CONFIRMED",
                                "attributes.arc_firmware_version": "1.0",
                            },
                            "verify": True,
                        },
                    ),
                    msg="GET method called incorrectly",
                )

    def test_assets_read_by_signature(self):
        """
        Test asset listing
        """
        with mock.patch.object(self.arch._session, "get") as mock_get:
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
                    (f"url/{ROOT}/{SUBPATH}",),
                    {
                        "headers": {
                            "authorization": "Bearer authauthauth",
                        },
                        "params": {"page_size": 2},
                        "verify": True,
                    },
                ),
                msg="GET method called incorrectly",
            )
