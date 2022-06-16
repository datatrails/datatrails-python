"""
Test archivist
"""

from copy import deepcopy
from logging import getLogger
from os import environ

from unittest import mock, TestCase

from archivist.archivist import Archivist
from archivist.constants import (
    ASSETS_LABEL,
    ASSETS_SUBPATH,
    ROOT,
)
from archivist.errors import ArchivistUnconfirmedError
from archivist.logger import set_logger

from .mock_response import MockResponse
from .testassetsconstants import (
    TestAssetsBaseConfirm,
    PRIMARY_IMAGE,
    ASSET_NAME,
    ATTRS,
    PROPS,
    REQUEST_KWARGS,
    RESPONSE,
)

PROPS_PUBLIC = {
    **PROPS,
    **{"public": True},
}
RESPONSE_PUBLIC = {
    **RESPONSE,
    **{"public": True},
}
REQUEST_KWARGS_PUBLIC = deepcopy(REQUEST_KWARGS)
REQUEST_KWARGS_PUBLIC["json"]["public"] = True
REQUEST_KWARGS_PUBLIC["headers"] = {}

# pylint: disable=missing-docstring
# pylint: disable=protected-access
# pylint: disable=unused-variable

if "TEST_DEBUG" in environ and environ["TEST_DEBUG"]:
    set_logger(environ["TEST_DEBUG"])

LOGGER = getLogger(__name__)


class TestPublicAssetsBase(TestCase):
    """
    Test Archivist Public Assets Base
    """

    maxDiff = None

    def setUp(self):
        self.arch = Archivist("url", None, max_time=1)

    def tearDown(self):
        self.arch = None


class TestPublicAssetsBaseConfirm(TestCase):
    """
    Test Archivist Public Assets Base
    """

    maxDiff = None

    def setUp(self):
        self.arch = Archivist("url", None, max_time=100)

    def tearDown(self):
        self.arch = None


class TestPublicAssetsUtil(TestPublicAssetsBase):
    """
    Test Archivist Public Assets utility
    """

    def test_public_assets_str(self):
        """
        Test assets str
        """
        self.assertEqual(
            str(self.arch.publicassets),
            "PublicAssetsClient(url)",
            msg="Incorrect str",
        )


class TestPublicAssetsCreate(TestPublicAssetsBase):
    """
    Test Archivist Public Assets methods
    """

    def test_publicassets_create(self):
        """
        Test public asset creation
        """
        with mock.patch.object(self.arch._session, "post", autospec=True) as mock_post:
            mock_post.return_value = MockResponse(200, **RESPONSE_PUBLIC)

            asset = self.arch.assets.create(
                props=PROPS_PUBLIC, attrs=ATTRS, confirm=False
            )
            args, kwargs = mock_post.call_args
            self.assertEqual(
                args,
                (f"url/{ROOT}/{ASSETS_SUBPATH}/{ASSETS_LABEL}",),
                msg="CREATE method args called incorrectly",
            )
            self.assertEqual(
                kwargs,
                REQUEST_KWARGS_PUBLIC,
                msg="CREATE method kwargs called incorrectly",
            )
            self.assertEqual(
                asset,
                RESPONSE_PUBLIC,
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

    def test_publicassets_create_with_confirmation_always_restricted_status(self):
        """
        Test public asset confirmation when public doe not appear
        """
        with mock.patch.object(
            self.arch._session, "post"
        ) as mock_post, mock.patch.object(self.arch._session, "get") as mock_get:
            mock_post.return_value = MockResponse(200, **RESPONSE)
            mock_get.side_effect = [
                MockResponse(200, **RESPONSE),
                MockResponse(200, **RESPONSE),
                MockResponse(200, **RESPONSE),
                MockResponse(200, **RESPONSE),
                MockResponse(200, **RESPONSE),
                MockResponse(200, **RESPONSE),
                MockResponse(200, **RESPONSE),
            ]
            with self.assertRaises(ArchivistUnconfirmedError):
                asset = self.arch.assets.create(
                    props=PROPS_PUBLIC, attrs=ATTRS, confirm=True
                )


class TestPublicAssetsCreateConfirm(TestAssetsBaseConfirm):
    """
    Test Archivist Assets methods with expected confirmation
    """

    def test_publicassets_create_with_confirmation(self):
        """
        Test asset creation
        """
        with mock.patch.object(
            self.arch._session, "post"
        ) as mock_post, mock.patch.object(self.arch._session, "get") as mock_get:
            mock_post.return_value = MockResponse(200, **RESPONSE_PUBLIC)
            mock_get.return_value = MockResponse(200, **RESPONSE_PUBLIC)
            asset = self.arch.assets.create(
                props=PROPS_PUBLIC, attrs=ATTRS, confirm=True
            )
            self.assertEqual(
                asset,
                RESPONSE_PUBLIC,
                msg="CREATE method called incorrectly",
            )

    def test_publicassets_create_with_explicit_confirmation(self):
        """
        Test asset creation
        """
        with mock.patch.object(
            self.arch._session, "post"
        ) as mock_post, mock.patch.object(self.arch._session, "get") as mock_get:
            mock_post.return_value = MockResponse(200, **RESPONSE_PUBLIC)
            mock_get.return_value = MockResponse(200, **RESPONSE_PUBLIC)
            asset = self.arch.assets.create(
                props=PROPS_PUBLIC, attrs=ATTRS, confirm=False
            )
            self.arch.assets.wait_for_confirmation(asset["identity"], public=True)
            self.assertEqual(
                asset,
                RESPONSE_PUBLIC,
                msg="CREATE method called incorrectly",
            )

    def test_publicassets_create_with_confirmation_public_status(self):
        """
        Test asset confirmation
        """
        with mock.patch.object(
            self.arch._session, "post"
        ) as mock_post, mock.patch.object(self.arch._session, "get") as mock_get:
            mock_post.return_value = MockResponse(200, **RESPONSE)
            mock_get.side_effect = [
                MockResponse(200, **RESPONSE),
                MockResponse(200, **RESPONSE_PUBLIC),
            ]
            asset = self.arch.assets.create(
                props=PROPS_PUBLIC, attrs=ATTRS, confirm=True
            )
            self.assertEqual(
                asset,
                RESPONSE_PUBLIC,
                msg="CREATE method called incorrectly",
            )
