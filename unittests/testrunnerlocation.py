"""
Test runner location
"""
from logging import getLogger
from os import environ
from unittest import TestCase, mock

# from archivist.errors import ArchivistBadRequestError

# pylint: disable=missing-docstring
# pylint: disable=protected-access
# pylint: disable=unused-variable

from archivist.archivist import Archivist
from archivist.locations import Location
from archivist.constants import LOCATIONS_LABEL
from archivist.logger import set_logger
from archivist.runner import Runner

if "TEST_DEBUG" in environ and environ["TEST_DEBUG"]:
    set_logger(environ["TEST_DEBUG"])

LOGGER = getLogger(__name__)

IDENTITY = f"{LOCATIONS_LABEL}/xxxxxxxx"
LOCATIONS_CREATE = {
    "selector": [
        "display_name",
    ],
    "display_name": "Macclesfield, Cheshire",
    "description": "Manufacturing site, North West England, Macclesfield, Cheshire",
    "latitude": "53.2546799",
    "longitude": "-2.1213956,14.54",
    "attributes": {
        "director": "John Smith",
        "address": "Bridgewater, Somerset",
        "facility_type": "Manufacture",
        "support_email": "support@macclesfield.com",
        "support_phone": "123 456 789",
    },
}
LOCATIONS_RESPONSE = {
    "identity": IDENTITY,
    "display_name": "Macclesfield, Cheshire",
    "description": "Manufacturing site, North West England, Macclesfield, Cheshire",
    "latitude": "53.2546799",
    "longitude": "-2.1213956,14.54",
    "attributes": {
        "director": "John Smith",
        "address": "Bridgewater, Somerset",
        "facility_type": "Manufacture",
        "support_email": "support@macclesfield.com",
        "support_phone": "123 456 789",
    },
}


class TestRunnerLocationsCreate(TestCase):
    """
    Test Archivist Runner
    """

    maxDiff = None

    def setUp(self):
        self.arch = Archivist("url", "authauthauth")
        self.runner = Runner()
        self.runner.entities["TestArchivist"] = self.arch

    def tearDown(self):
        self.arch.close()

    @mock.patch("archivist.runner.time_sleep")
    def test_runner_locations_create(self, mock_sleep):
        """
        Test runner operation
        """
        with mock.patch.object(
            self.arch.locations, "create_if_not_exists"
        ) as mock_locations_create:
            mock_locations_create.return_value = Location(**LOCATIONS_RESPONSE)
            self.runner(
                {
                    "steps": [
                        {
                            "step": {
                                "action": "LOCATIONS_CREATE_IF_NOT_EXISTS",
                                "wait_time": 10,
                                "description": "Testing runner locations create",
                                "archivist_label": "TestArchivist",
                                "location_label": "Existing Location",
                            },
                            **LOCATIONS_CREATE,
                        },
                    ],
                }
            )
            mock_locations_create.assert_called_once_with(LOCATIONS_CREATE)
            mock_sleep.assert_called_once_with(10)
