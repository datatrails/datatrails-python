"""
Test tenancies read
"""

from logging import getLogger
from os import environ
from unittest import mock, TestCase

from archivist.archivist import Archivist
from archivist.constants import (
    ROOT,
    TENANCIES_LABEL,
    TENANCIES_PREFIX,
    TENANCIES_SUBPATH,
)
from archivist.logger import set_logger

from .mock_response import MockResponse

IDENTITY = f"{TENANCIES_LABEL}/c3da0d3a-32bf-4f5f-a8c6-b342a8356480"
RESPONSE_IDENTITY = f"{TENANCIES_PREFIX}/c3da0d3a-32bf-4f5f-a8c6-b342a8356480"
VERIFIED_DOMAIN = "info.acme.com"
RESPONSE_PUBLICINFO = {
    "identity": IDENTITY,
    "verified_domain": VERIFIED_DOMAIN,
}

# pylint: disable=missing-docstring
# pylint: disable=protected-access
# pylint: disable=unused-variable

if "RKVST_DEBUG" in environ and environ["RKVST_DEBUG"]:
    set_logger(environ["RKVST_DEBUG"])

LOGGER = getLogger(__name__)


class TestTenanciesBase(TestCase):
    """
    Test Archivist Tenancies Base
    """

    maxDiff = None

    def setUp(self):
        self.arch = Archivist("url", "authauthauth", max_time=1)

    def tearDown(self):
        self.arch.close()


class TestTenanciesRead(TestTenanciesBase):
    """
    Test Archivist Tenancies methods
    """

    def test_tenancies_str(self):
        """
        Test tenancies str
        """
        self.assertEqual(
            str(self.arch.tenancies),
            "TenanciesClient(url)",
            msg="Incorrect str",
        )

    def test_tenancies_publicinfo(self):
        """
        Test tenancy reading publicinfo
        """
        with mock.patch.object(self.arch.session, "get") as mock_get:
            mock_get.return_value = MockResponse(200, **RESPONSE_PUBLICINFO)

            publicinfo = self.arch.tenancies.publicinfo(IDENTITY)
            args, kwargs = mock_get.call_args
            self.assertEqual(
                args,
                (f"url/{ROOT}/{TENANCIES_SUBPATH}/{IDENTITY}:publicinfo",),
                msg="GET method args called incorrectly",
            )
            self.assertEqual(
                kwargs,
                {
                    "params": None,
                    "headers": {
                        "authorization": "Bearer authauthauth",
                    },
                    "verify": True,
                },
                msg="GET method kwargs called incorrectly",
            )
            self.assertEqual(
                publicinfo,
                RESPONSE_PUBLICINFO,
                msg="Public info is incorrect",
            )

    def test_tenancies_publicinfo_response_identity(self):
        """
        Test tenancy reading publicinfo
        """
        with mock.patch.object(self.arch.session, "get") as mock_get:
            mock_get.return_value = MockResponse(200, **RESPONSE_PUBLICINFO)

            publicinfo = self.arch.tenancies.publicinfo(RESPONSE_IDENTITY)
            args, kwargs = mock_get.call_args
            self.assertEqual(
                args,
                (f"url/{ROOT}/{TENANCIES_SUBPATH}/{IDENTITY}:publicinfo",),
                msg="GET method args called incorrectly",
            )
            self.assertEqual(
                kwargs,
                {
                    "params": None,
                    "headers": {
                        "authorization": "Bearer authauthauth",
                    },
                    "verify": True,
                },
                msg="GET method kwargs called incorrectly",
            )
            self.assertEqual(
                publicinfo,
                RESPONSE_PUBLICINFO,
                msg="Public info is incorrect",
            )
