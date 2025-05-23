"""
Test appidp
"""

from unittest import TestCase, mock

from archivist.about import __version__ as VERSION
from archivist.archivist import Archivist
from archivist.constants import (
    APPIDP_LABEL,
    APPIDP_SUBPATH,
    APPIDP_TOKEN,
    ROOT,
    USER_AGENT,
    USER_AGENT_PREFIX,
)

from .mock_response import MockResponse

# pylint: disable=missing-docstring
# pylint: disable=protected-access
# pylint: disable=unused-variable

SUBPATH = f"{APPIDP_SUBPATH}/{APPIDP_LABEL}/{APPIDP_TOKEN}"
DATATRAILS_APPREG_CLIENT = "client_id-2f78-4fa0-9425-d59314845bc5"
DATATRAILS_APPREG_SECRET = "client_secret-388f5187e32d930d83"
ACCESS_TOKEN = "access_token-xbXATAWrEpepR7TklOxRB-yud92AsD6DGGasiEGN7MZKT0AIQ4Rw9s"
REQUEST = {
    "grant_type": "client_credentials",
    "client_id": DATATRAILS_APPREG_CLIENT,
    "client_secret": DATATRAILS_APPREG_SECRET,
}

RESPONSE = {
    "access_token": ACCESS_TOKEN,
    "expires_in": 660,
    "token_type": "Bearer",
}


class TestAppIDP(TestCase):
    """
    Test Archivist AppIDP token method
    """

    maxDiff = None

    def setUp(self):
        self.arch = Archivist("url", "authauthauth")

    def tearDown(self):
        self.arch.close()

    def test_appidp_str(self):
        """
        Test appidp str
        """
        self.assertEqual(
            str(self.arch.appidp),
            "AppIDPClient(url)",
            msg="Incorrect str",
        )

    def test_appidp_token_create(self):
        """
        Test appidp token
        """
        with mock.patch.object(self.arch.session, "post") as mock_post:
            mock_post.return_value = MockResponse(200, **RESPONSE)

            appidp = self.arch.appidp.token(
                DATATRAILS_APPREG_CLIENT,
                DATATRAILS_APPREG_SECRET,
            )
            args, kwargs = mock_post.call_args
            self.assertEqual(
                args,
                (f"url/{ROOT}/{SUBPATH}",),
                msg="CREATE method args called incorrectly",
            )
            self.assertEqual(
                kwargs,
                {
                    "headers": {
                        USER_AGENT: f"{USER_AGENT_PREFIX}{VERSION}",
                    },
                    "data": REQUEST,
                },
                msg="CREATE method kwargs called incorrectly",
            )
            self.assertEqual(
                appidp,
                RESPONSE,
                msg="TOKEN method called incorrectly",
            )
