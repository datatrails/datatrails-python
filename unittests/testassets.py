"""
Test assets
"""

from copy import copy
from logging import getLogger
from os import environ
from unittest import mock

from archivist.constants import (
    ASSETS_LABEL,
    ASSETS_SUBPATH,
    ROOT,
)
from archivist.errors import ArchivistNotFoundError, ArchivistUnconfirmedError
from archivist.logger import set_logger

from .mock_response import MockResponse
from .testassetsconstants import (
    ASSET_NAME,
    ATTRS,
    FIXTURES,
    MERKLE_LOG,
    PRIMARY_IMAGE,
    REQUEST_EXISTS,
    REQUEST_EXISTS_ATTACHMENTS,
    REQUEST_EXISTS_KWARGS,
    REQUEST_EXISTS_KWARGS_ATTACHMENTS,
    REQUEST_EXISTS_KWARGS_LOCATION,
    REQUEST_EXISTS_LOCATION,
    REQUEST_EXISTS_LOCATION_IDENTITY,
    REQUEST_FIXTURES_KWARGS,
    REQUEST_KWARGS,
    REQUEST_KWARGS_MERKLE_LOG,
    RESPONSE,
    RESPONSE_ATTACHMENTS,
    RESPONSE_EXISTS,
    RESPONSE_EXISTS_ATTACHMENTS,
    RESPONSE_EXISTS_LOCATION,
    RESPONSE_FAILED,
    RESPONSE_FIXTURES,
    RESPONSE_LOCATION,
    RESPONSE_NO_CONFIRMATION,
    RESPONSE_PENDING,
    RESPONSE_UNEQUIVOCAL,
    SUBPATH,
    TestAssetsBase,
    TestAssetsBaseConfirm,
)

# pylint: disable=missing-docstring
# pylint: disable=protected-access
# pylint: disable=unused-variable

if "DATATRAILS_LOGLEVEL" in environ and environ["DATATRAILS_LOGLEVEL"]:
    set_logger(environ["DATATRAILS_LOGLEVEL"])

LOGGER = getLogger(__name__)


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
            "AssetsRestricted(url)",
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
        with mock.patch.object(self.arch.session, "post", autospec=True) as mock_post:
            mock_post.return_value = MockResponse(200, **RESPONSE)

            asset = self.arch.assets.create(attrs=ATTRS, confirm=False)
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

    def test_assets_create_merkle_log(self):
        """
        Test asset creation specifying merkle log mechanism
        """
        with mock.patch.object(self.arch.session, "post", autospec=True) as mock_post:
            mock_post.return_value = MockResponse(200, **RESPONSE)

            asset = self.arch.assets.create(
                props=MERKLE_LOG, attrs=ATTRS, confirm=False
            )
            args, kwargs = mock_post.call_args
            self.assertEqual(
                args,
                (f"url/{ROOT}/{ASSETS_SUBPATH}/{ASSETS_LABEL}",),
                msg="CREATE method args called incorrectly",
            )
            self.assertEqual(
                kwargs,
                REQUEST_KWARGS_MERKLE_LOG,
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
        with mock.patch.object(arch.session, "post", autospec=True) as mock_post:
            mock_post.return_value = MockResponse(200, **RESPONSE_FIXTURES)
            asset = arch.assets.create(attrs=ATTRS, confirm=False)
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

    def test_assets_create_with_confirmation_no_confirmed_status(self):
        """
        Test asset confirmation
        """
        with mock.patch.object(
            self.arch.session, "post"
        ) as mock_post, mock.patch.object(self.arch.session, "get") as mock_get:
            mock_post.return_value = MockResponse(200, **RESPONSE)
            mock_get.return_value = MockResponse(200, **RESPONSE_NO_CONFIRMATION)

            with self.assertRaises(ArchivistUnconfirmedError):
                self.arch.assets.create(attrs=ATTRS, confirm=True)

    def test_assets_create_with_confirmation_failed_status(self):
        """
        Test asset confirmation
        """
        with mock.patch.object(
            self.arch.session, "post"
        ) as mock_post, mock.patch.object(self.arch.session, "get") as mock_get:
            mock_post.return_value = MockResponse(200, **RESPONSE)
            mock_get.side_effect = [
                MockResponse(200, **RESPONSE_PENDING),
                MockResponse(200, **RESPONSE_FAILED),
            ]
            with self.assertRaises(ArchivistUnconfirmedError):
                self.arch.assets.create(attrs=ATTRS, confirm=True)

    def test_assets_create_with_confirmation_always_pending_status(self):
        """
        Test asset confirmation
        """
        with mock.patch.object(
            self.arch.session, "post"
        ) as mock_post, mock.patch.object(self.arch.session, "get") as mock_get:
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
                self.arch.assets.create(attrs=ATTRS, confirm=True)


class TestAssetsCreateConfirm(TestAssetsBaseConfirm):
    """
    Test Archivist Assets methods with expected confirmation
    """

    def test_assets_create_with_confirmation(self):
        """
        Test asset creation
        """
        with mock.patch.object(
            self.arch.session, "post"
        ) as mock_post, mock.patch.object(self.arch.session, "get") as mock_get:
            mock_post.return_value = MockResponse(200, **RESPONSE)
            mock_get.return_value = MockResponse(200, **RESPONSE)
            asset = self.arch.assets.create(attrs=ATTRS, confirm=True)
            self.assertEqual(
                asset,
                RESPONSE,
                msg="CREATE method called incorrectly",
            )

    def test_assets_create_with_confirmation_unequivocal(self):
        """
        Test asset creation
        """
        with mock.patch.object(
            self.arch.session, "post"
        ) as mock_post, mock.patch.object(self.arch.session, "get") as mock_get:
            mock_post.return_value = MockResponse(200, **RESPONSE_UNEQUIVOCAL)
            mock_get.return_value = MockResponse(200, **RESPONSE_UNEQUIVOCAL)
            asset = self.arch.assets.create(attrs=ATTRS, confirm=True)
            self.assertEqual(
                asset,
                RESPONSE_UNEQUIVOCAL,
                msg="CREATE method called incorrectly",
            )

    def test_assets_create_with_explicit_confirmation(self):
        """
        Test asset creation
        """
        with mock.patch.object(
            self.arch.session, "post"
        ) as mock_post, mock.patch.object(self.arch.session, "get") as mock_get:
            mock_post.return_value = MockResponse(200, **RESPONSE)
            mock_get.return_value = MockResponse(200, **RESPONSE)
            asset = self.arch.assets.create(attrs=ATTRS, confirm=False)
            self.arch.assets.wait_for_confirmation(asset["identity"])
            self.assertEqual(
                asset,
                RESPONSE,
                msg="CREATE method called incorrectly",
            )

    def test_assets_create_with_confirmation_pending_status(self):
        """
        Test asset confirmation
        """
        with mock.patch.object(
            self.arch.session, "post"
        ) as mock_post, mock.patch.object(self.arch.session, "get") as mock_get:
            mock_post.return_value = MockResponse(200, **RESPONSE)
            mock_get.side_effect = [
                MockResponse(200, **RESPONSE_PENDING),
                MockResponse(200, **RESPONSE),
            ]
            asset = self.arch.assets.create(attrs=ATTRS, confirm=True)
            self.assertEqual(
                asset,
                RESPONSE,
                msg="CREATE method called incorrectly",
            )


class TestAssetsCreateIfNotExists(TestAssetsBase):
    """
    Test Archivist Assets methods
    """

    def test_assets_create_if_not_exists_existing_asset(self):
        """
        Test asset creation
        """
        with mock.patch.object(
            self.arch.session, "post", autospec=True
        ) as mock_post, mock.patch.object(self.arch.session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                assets=[
                    RESPONSE_EXISTS,
                ],
            )
            mock_post.return_value = MockResponse(200, **RESPONSE)

            asset, existed = self.arch.assets.create_if_not_exists(
                data=REQUEST_EXISTS,
                confirm=False,
            )
            mock_post.assert_not_called()
            self.assertEqual(
                existed,
                True,
                msg="Incorrect existed bool",
            )
            self.assertEqual(
                asset,
                RESPONSE_EXISTS,
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
                        "params": {
                            "attributes.arc_namespace": "namespace",
                            "attributes.arc_display_name": "tcl.ppj.003",
                            "page_size": 2,
                        },
                    },
                ),
                msg="GET method called incorrectly",
            )

    def common_assets_create_if_not_exists_nonexistent_asset(
        self,
        req,
        req_kwargs,
        resp,
        loc_resp=None,
        attachments_resp=None,
    ):
        """
        Test asset creation
        """
        with mock.patch.object(
            self.arch.session, "post", autospec=True
        ) as mock_post, mock.patch.object(
            self.arch.session, "get"
        ) as mock_get, mock.patch.object(
            self.arch.locations, "create_if_not_exists"
        ) as mock_location, mock.patch.object(
            self.arch.attachments, "create"
        ) as mock_attachments:
            mock_get.side_effect = ArchivistNotFoundError
            mock_post.return_value = MockResponse(200, **resp)
            if loc_resp is not None:
                mock_location.return_value = (MockResponse(200, **loc_resp), True)

            if attachments_resp is not None:
                mock_attachments.return_value = MockResponse(200, **attachments_resp)

            asset, existed = self.arch.assets.create_if_not_exists(
                data=req,
                confirm=False,
            )
            mock_get.assert_called_once()
            mock_post.assert_called_once()

            self.assertEqual(
                existed,
                False,
                msg="Incorrect existed bool",
            )
            args, kwargs = mock_post.call_args
            self.assertEqual(
                args,
                (f"url/{ROOT}/{ASSETS_SUBPATH}/{ASSETS_LABEL}",),
                msg="CREATE method args called incorrectly",
            )
            self.assertEqual(
                kwargs,
                req_kwargs,
                msg="CREATE method kwargs called incorrectly",
            )
            self.assertEqual(
                asset,
                resp,
                msg="CREATE method called incorrectly",
            )

            if attachments_resp is not None:
                mock_attachments.assert_called()
                args, kwargs = mock_attachments.call_args_list[0]
                self.assertEqual(
                    args,
                    (req.get("attachments")[0],),
                    msg="CREATE_ATTACHMENTS method args called incorrectly",
                )
                self.assertEqual(
                    kwargs,
                    {},
                    msg="CREATE_ATTACHMENTS method kwargs called incorrectly",
                )

            if loc_resp is not None:
                mock_location.assert_called_once()
                args, kwargs = mock_location.call_args
                self.assertEqual(
                    args,
                    (req.get("location"),),
                    msg="CREATE_LOCATION method args called incorrectly",
                )
                self.assertEqual(
                    kwargs,
                    {},
                    msg="CREATE_LOCATION method kwargs called incorrectly",
                )

    def test_assets_create_if_not_exists_nonexistent_asset(self):
        """
        Test asset creation
        """
        self.common_assets_create_if_not_exists_nonexistent_asset(
            REQUEST_EXISTS,
            REQUEST_EXISTS_KWARGS,
            RESPONSE_EXISTS,
        )

    def test_assets_create_if_not_exists_nonexistent_asset_location(self):
        """
        Test asset creation
        """
        self.common_assets_create_if_not_exists_nonexistent_asset(
            REQUEST_EXISTS_LOCATION,
            REQUEST_EXISTS_KWARGS_LOCATION,
            RESPONSE_EXISTS_LOCATION,
            loc_resp=RESPONSE_LOCATION,
        )

    def test_assets_create_if_not_exists_nonexistent_asset_location_identity(self):
        """
        Test asset creation
        """
        self.common_assets_create_if_not_exists_nonexistent_asset(
            REQUEST_EXISTS_LOCATION_IDENTITY,
            REQUEST_EXISTS_KWARGS_LOCATION,
            RESPONSE_EXISTS_LOCATION,
        )

    def test_assets_create_if_not_exists_nonexistent_asset_attachments(self):
        """
        Test asset creation
        """
        self.common_assets_create_if_not_exists_nonexistent_asset(
            REQUEST_EXISTS_ATTACHMENTS,
            REQUEST_EXISTS_KWARGS_ATTACHMENTS,
            RESPONSE_EXISTS_ATTACHMENTS,
            attachments_resp=RESPONSE_ATTACHMENTS,
        )
