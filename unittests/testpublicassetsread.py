"""
Test public assets read
"""

from logging import getLogger
from os import environ
from unittest import mock

from archivist.about import __version__ as VERSION
from archivist.constants import (
    ROOT,
    USER_AGENT,
    USER_AGENT_PREFIX,
)
from archivist.logger import set_logger

from .mock_response import MockResponse
from .testassetsconstants import (
    IDENTITY,
    RESPONSE_NO_ATTACHMENTS,
)
from .testpublicassets import (
    TestPublicAssetsBase,
)

# pylint: disable=missing-docstring
# pylint: disable=protected-access
# pylint: disable=unused-variable

if "DATATRAILS_LOGLEVEL" in environ and environ["DATATRAILS_LOGLEVEL"]:
    set_logger(environ["DATATRAILS_LOGLEVEL"])

LOGGER = getLogger(__name__)

URL = "https://app.datatrails.ai"
ASSET_ID = f"{URL}/{ROOT}/public{IDENTITY}"
SUBPATH = f"public{IDENTITY}"

ASSET_ID_NO_SUBPATH = f"{URL}/{ROOT}/public{IDENTITY}"
NO_SUBPATH = f"public{IDENTITY}"


class TestPublicAssetsRead(TestPublicAssetsBase):
    """
    Test Archivist Assets methods
    """

    def test_publicassets_read(self):
        """
        Test asset reading
        """
        with mock.patch.object(self.public.session, "get") as mock_get:
            mock_get.return_value = MockResponse(200, **RESPONSE_NO_ATTACHMENTS)

            asset = self.public.assets.read(ASSET_ID)
            self.assertEqual(
                asset,
                RESPONSE_NO_ATTACHMENTS,
                msg="READ method called incorrectly",
            )
            args, kwargs = mock_get.call_args
            self.assertEqual(
                args,
                (f"{URL}/{ROOT}/{SUBPATH}",),
                msg="GET method args called incorrectly",
            )
            self.assertEqual(
                kwargs,
                {
                    "headers": {
                        USER_AGENT: f"{USER_AGENT_PREFIX}{VERSION}",
                    },
                    "params": None,
                },
                msg="GET method kwargs called incorrectly",
            )
