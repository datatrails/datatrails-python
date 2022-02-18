"""
Test runner
"""
from logging import getLogger
from os import environ
from unittest import TestCase, mock

# from archivist.errors import ArchivistBadRequestError

# pylint: disable=missing-docstring
# pylint: disable=protected-access
# pylint: disable=unused-variable

from archivist.archivist import Archivist
from archivist.assets import Asset
from archivist.errors import ArchivistInvalidOperationError
from archivist.logger import set_logger

if "TEST_DEBUG" in environ and environ["TEST_DEBUG"]:
    set_logger(environ["TEST_DEBUG"])

LOGGER = getLogger(__name__)

ASSET_ID = "assets/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
ASSET_NAME = "radiation bag 1"
ASSETS_CREATE_ARGS = {
    "behaviours": ["RecordEvidence", "Attachments"],
    "attributes": {
        "arc_display_name": ASSET_NAME,
        "radioactive": True,
        "radiation_level": 0,
        "weight": 0,
    },
}
ASSETS_CONFIRM = {
    "confirm": True,
}
ASSETS_CREATE = {
    **ASSETS_CREATE_ARGS,
    **ASSETS_CONFIRM,
}

ASSETS_RESPONSE = {
    "attributes": {
        "arc_display_name": ASSET_NAME,
        "radioactive": True,
        "radiation_level": 0,
        "weight": 0,
    },
    "behaviours": ["Attachments", "RecordEvidence"],
    "confirmation_status": "CONFIRMED",
    "identity": ASSET_ID,
}

ASSETS_NO_NAME_RESPONSE = {
    "attributes": {
        "radioactive": True,
        "radiation_level": 0,
        "weight": 0,
    },
    "behaviours": ["Attachments", "RecordEvidence"],
    "confirmation_status": "CONFIRMED",
    "identity": ASSET_ID,
}


class TestRunnerAssetsCreate(TestCase):
    """
    Test Archivist Runner
    """

    maxDiff = None

    def setUp(self):
        self.arch = Archivist("url", "authauthauth")

    @mock.patch("archivist.runner.time_sleep")
    def test_runner_assets_create(self, mock_sleep):
        """
        Test runner operation
        """
        with mock.patch.object(
            self.arch.assets, "create_from_data"
        ) as mock_assets_create:
            mock_assets_create.return_value = Asset(**ASSETS_RESPONSE)
            self.arch.runner(
                {
                    "steps": [
                        {
                            "step": {
                                "action": "ASSETS_CREATE",
                                "wait_time": 10,
                                "description": "Testing runner assets create",
                            },
                            **ASSETS_CREATE,
                        },
                    ],
                }
            )
            mock_sleep.assert_called_once_with(10)
            mock_assets_create.assert_called_once_with(
                ASSETS_CREATE_ARGS, **ASSETS_CONFIRM
            )
            self.assertEqual(
                self.arch.runner.entities["ASSETS_CREATE"][ASSET_NAME],
                ASSETS_RESPONSE,
                msg="Incorrect asset created",
            )

    @mock.patch("archivist.runner.time_sleep")
    def test_runner_assets_create_no_wait(self, mock_sleep):
        """
        Test runner operation
        """
        with mock.patch.object(
            self.arch.assets, "create_from_data"
        ) as mock_assets_create:
            mock_assets_create.return_value = Asset(**ASSETS_RESPONSE)
            self.arch.runner.run_steps(
                {
                    "steps": [
                        {
                            "step": {
                                "action": "ASSETS_CREATE",
                            },
                            **ASSETS_CREATE,
                        },
                    ],
                }
            )
            self.assertEqual(
                mock_sleep.call_count,
                0,
                msg="time_sleep incorrectly called",
            )
            mock_assets_create.assert_called_once_with(
                ASSETS_CREATE_ARGS, **ASSETS_CONFIRM
            )

    def test_runner_assets_create_no_action(self):
        """
        Test runner operation
        """
        with mock.patch.object(
            self.arch.assets, "create_from_data"
        ) as mock_assets_create:
            mock_assets_create.return_value = Asset(**ASSETS_RESPONSE)
            with self.assertRaises(ArchivistInvalidOperationError) as ex:
                self.arch.runner.run_steps(
                    {
                        "steps": [
                            {
                                "step": {
                                    "wait_time": 10,
                                },
                                **ASSETS_CREATE,
                            }
                        ],
                    }
                )

            self.assertEqual("Missing Action" in str(ex.exception), True)

    def test_runner_assets_create_invalid_action(self):
        """
        Test runner operation
        """
        with mock.patch.object(
            self.arch.assets, "create_from_data"
        ) as mock_assets_create:
            mock_assets_create.return_value = Asset(**ASSETS_RESPONSE)
            with self.assertRaises(ArchivistInvalidOperationError) as ex:
                self.arch.runner.run_steps(
                    {
                        "steps": [
                            {
                                "step": {
                                    "action": "ASSETSS_CREATE",
                                },
                                **ASSETS_CREATE,
                            }
                        ],
                    }
                )

            self.assertEqual("Action ASSETSS" in str(ex.exception), True)

    @mock.patch("archivist.runner.time_sleep")
    def test_runner_assets_create_invalid_verb_caught(self, mock_sleep):
        """
        Test runner operation
        """
        with mock.patch.object(
            self.arch.assets, "create_from_data"
        ) as mock_assets_create:
            mock_assets_create.return_value = Asset(**ASSETS_RESPONSE)
            self.arch.runner(
                {
                    "steps": [
                        {
                            "step": {
                                "action": "ASSETSS_CREATE",
                            },
                            **ASSETS_CREATE,
                        }
                    ],
                }
            )
            self.assertEqual(
                mock_sleep.call_count,
                0,
                msg="time_sleep incorrectly called",
            )
            self.assertEqual(
                mock_assets_create.call_count,
                0,
                msg="assets.create incorrectly called",
            )
