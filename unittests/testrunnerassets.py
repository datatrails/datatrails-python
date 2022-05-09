"""
Test runner assets
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
from archivist.constants import ASSET_BEHAVIOURS
from archivist.errors import ArchivistInvalidOperationError
from archivist.events import Event
from archivist.logger import set_logger
from archivist.runner import Runner

if "TEST_DEBUG" in environ and environ["TEST_DEBUG"]:
    set_logger(environ["TEST_DEBUG"])

LOGGER = getLogger(__name__)

ASSET_ID = "assets/add30235-1424-4fda-840a-d5ef82c4c96f"
ASSET_NAME = "radiation bag 1"
ASSETS_CREATE_ARGS = {
    "behaviours": ASSET_BEHAVIOURS,
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
}
ASSETS_CREATE_IF_NOT_EXISTS = {
    "selector": {
        "attributes.arc_display_name",
    },
    "behaviours": ASSET_BEHAVIOURS,
    "attributes": {
        "arc_display_name": ASSET_NAME,
        "radioactive": True,
        "radiation_level": 0,
        "weight": 0,
    },
}

ASSETS_RESPONSE = {
    "attributes": {
        "arc_display_name": ASSET_NAME,
        "radioactive": True,
        "radiation_level": 0,
        "weight": 0,
    },
    "behaviours": ASSET_BEHAVIOURS,
    "confirmation_status": "CONFIRMED",
    "identity": ASSET_ID,
}

ASSETS_NO_NAME_RESPONSE = {
    "attributes": {
        "radioactive": True,
        "radiation_level": 0,
        "weight": 0,
    },
    "behaviours": ASSET_BEHAVIOURS,
    "confirmation_status": "CONFIRMED",
    "identity": ASSET_ID,
}

EVENTS_LIST = {
    "props": {
        "confirmation_status": "CONFIRMED",
    },
    "attrs": {
        "arc_display_type": "open",
    },
    "asset_attrs": {
        "arc_display_type": "door",
    },
}
EVENTS_LIST_ASSET_ID = "assets/add30235-1424-4fda-840a-d5ef82c4c96f"
EVENTS_LIST_PROPS = {
    "confirmation_status": "CONFIRMED",
}
EVENTS_LIST_ATTRS = {
    "arc_display_type": "open",
}
EVENTS_LIST_ASSET_ATTRS = {
    "arc_display_type": "door",
}
EVENTS_CREATE = {
    "asset_identity": "assets/add30235-1424-4fda-840a-d5ef82c4c96f",
    "operation": "Record",
    "behaviour": "RecordEvidence",
    "event_attributes": {
        "arc_display_type": "open",
        "arc_attachments": [
            {
                "arc_attachment_identity": "blobs/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
                "arc_display_name": "an attachment 1",
                "arc_hash_value": "jnwpjocoqsssnundwlqalsqiiqsqp;lpiwpldkndwwlskqaalijopjkokkkijl",
                "arc_hash_alg": "sha256",
            },
            {
                "arc_attachment_identity": "blobs/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
                "arc_display_name": "an attachment 2",
                "arc_hash_value": "042aea10a0f14f2d391373599be69d53a75dde9951fc3d3cd10b6100aa7f24",
                "arc_hash_alg": "sha256",
            },
        ],
    },
    "location": {"identity": "locations/add30235-1424-4fda-840a-d5ef82c4c96f"},
}
EVENT_RESPONSE = {
    "identity": (
        "assets/add30235-1424-4fda-840a-d5ef82c4c96f/"
        "events/11bf5b37-e0b8-42e0-8dcf-dc8c4aefc000"
    ),
    "asset_identity": "assets/add30235-1424-4fda-840a-d5ef82c4c96f",
    "operation": "Record",
    "behaviour": "RecordEvidence",
    "event_attributes": {
        "arc_display_type": "open",
        "arc_attachments": [
            {
                "arc_attachment_identity": "blobs/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
                "arc_display_name": "an attachment 1",
                "arc_hash_value": "jnwpjocoqsssnundwlqalsqiiqsqp;lpiwpldkndwwlskqaalijopjkokkkijl",
                "arc_hash_alg": "sha256",
            },
            {
                "arc_attachment_identity": "blobs/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
                "arc_display_name": "an attachment 2",
                "arc_hash_value": "042aea10a0f14f2d391373599be69d53a75dde9951fc3d3cd10b6100aa7f24",
                "arc_hash_alg": "sha256",
            },
        ],
    },
    "asset_attributes": {
        "arc_display_type": "door",
    },
    "timestamp_accepted": "2019-11-27T15:13:21Z",
    "timestamp_declared": "2019-11-27T14:44:19Z",
    "timestamp_committed": "2019-11-27T15:15:02Z",
    "principal_declared": {
        "issuer": "idp.synsation.io/1234",
        "subject": "phil.b",
        "email": "phil.b@synsation.io",
    },
    "principal_accepted": {"issuer": "job.idp.server/1234", "subject": "bob@job"},
    "confirmation_status": "CONFIRMED",
    "block_number": 12,
    "transaction_index": 5,
    "transaction_id": "0x07569",
}
LOCATION_IDENTITY = "locations/add30235-1424-4fda-840a-d5ef82c4c96f"
LOCATION_IDENTITY_BAD_UUID = "locations/add30235-xxxx-xxxx-xxxx-d5ef82c4c96f"


def event_generator(n: int):
    for i in range(n):
        yield EVENT_RESPONSE


class TestRunnerAssetsCreate(TestCase):
    """
    Test Archivist Runner
    """

    maxDiff = None

    def setUp(self):
        self.arch = Archivist("https://app.rkvst.io", "authauthauth")
        self.runner = Runner()
        self.runner.entities["TestArchivist"] = self.arch
        self.runner.entities[ASSET_NAME] = ASSETS_RESPONSE

    def tearDown(self):
        self.arch.close()

    @mock.patch("archivist.runner.time_sleep")
    def test_runner_assets_create(self, mock_sleep):
        """
        Test runner operation
        """
        with mock.patch.object(
            self.arch.assets, "create_from_data"
        ) as mock_assets_create:
            mock_assets_create.return_value = Asset(**ASSETS_RESPONSE)
            self.runner(
                {
                    "steps": [
                        {
                            "step": {
                                "action": "ASSETS_CREATE",
                                "wait_time": 10,
                                "description": "Testing runner assets create",
                                "delete": True,
                                "archivist_label": "TestArchivist",
                                "asset_label": ASSET_NAME,
                            },
                            **ASSETS_CREATE,
                        },
                    ],
                }
            )
            mock_assets_create.assert_called_once_with(ASSETS_CREATE_ARGS)
            mock_sleep.assert_called_once_with(10)

    @mock.patch("archivist.runner.time_sleep")
    def test_runner_assets_create_if_not_exists(self, mock_sleep):
        """
        Test runner operation
        """
        with mock.patch.object(
            self.arch.assets, "create_if_not_exists"
        ) as mock_assets_create:
            mock_assets_create.return_value = (Asset(**ASSETS_RESPONSE), True)
            self.runner(
                {
                    "steps": [
                        {
                            "step": {
                                "action": "ASSETS_CREATE_IF_NOT_EXISTS",
                                "wait_time": 10,
                                "description": "Testing runner assets create if not exists",
                                "asset_label": ASSET_NAME,
                                "archivist_label": "TestArchivist",
                            },
                            **ASSETS_CREATE_IF_NOT_EXISTS,
                            "confirm": True,
                        },
                    ],
                }
            )
            mock_assets_create.assert_called_once_with(
                ASSETS_CREATE_IF_NOT_EXISTS, **ASSETS_CONFIRM
            )
            mock_sleep.assert_called_once_with(10)

    @mock.patch("archivist.runner.time_sleep")
    def test_runner_events_list(self, mock_sleep):
        """
        Test runner operation
        """
        with mock.patch.object(self.arch.events, "list") as mock_events_list:
            mock_events_list.return_value = event_generator(2)
            self.runner(
                {
                    "steps": [
                        {
                            "step": {
                                "action": "EVENTS_LIST",
                                "wait_time": 10,
                                "print_response": True,
                                "description": "Testing runner events list",
                                "asset_label": ASSET_NAME,
                                "archivist_label": "TestArchivist",
                            },
                            **EVENTS_LIST,
                        },
                    ],
                }
            )
            mock_events_list.assert_called_once_with(
                asset_id=EVENTS_LIST_ASSET_ID,
                props=EVENTS_LIST_PROPS,
                attrs=EVENTS_LIST_ATTRS,
                asset_attrs=EVENTS_LIST_ASSET_ATTRS,
            )
            mock_sleep.assert_called_once_with(10)

    @mock.patch("archivist.runner.time_sleep")
    def test_runner_events_count(self, mock_sleep):
        """
        Test runner operation
        """
        with mock.patch.object(self.arch.events, "count") as mock_events_count:
            mock_events_count.return_value = 2
            self.runner(
                {
                    "steps": [
                        {
                            "step": {
                                "action": "EVENTS_COUNT",
                                "wait_time": 10,
                                "print_response": True,
                                "description": "Testing runner events count",
                                "asset_label": ASSET_NAME,
                                "archivist_label": "TestArchivist",
                            },
                            **EVENTS_LIST,
                        },
                    ],
                }
            )
            mock_events_count.assert_called_once_with(
                asset_id=EVENTS_LIST_ASSET_ID,
                props=EVENTS_LIST_PROPS,
                attrs=EVENTS_LIST_ATTRS,
                asset_attrs=EVENTS_LIST_ASSET_ATTRS,
            )
            mock_sleep.assert_called_once_with(10)

    @mock.patch("archivist.runner.time_sleep")
    def test_runner_assets_create_no_wait(self, mock_sleep):
        """
        Test runner operation
        """
        with mock.patch.object(
            self.arch.assets, "create_from_data"
        ) as mock_assets_create:
            mock_assets_create.return_value = Asset(**ASSETS_RESPONSE)
            self.runner.run_steps(
                {
                    "steps": [
                        {
                            "step": {
                                "action": "ASSETS_CREATE",
                                "archivist_label": "TestArchivist",
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
            mock_assets_create.assert_called_once_with(ASSETS_CREATE_ARGS)

    def test_runner_assets_create_no_action(self):
        """
        Test runner operation
        """
        with mock.patch.object(
            self.arch.assets, "create_from_data"
        ) as mock_assets_create:
            mock_assets_create.return_value = Asset(**ASSETS_RESPONSE)
            with self.assertRaises(ArchivistInvalidOperationError) as ex:
                self.runner.run_steps(
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

    def test_runner_events_create_illegal_asset_label(self):
        """
        Test runner operation
        """
        with mock.patch.object(
            self.arch.events, "create_from_data"
        ) as mock_events_create:
            mock_events_create.return_value = Event(**EVENT_RESPONSE)
            with self.assertRaises(ArchivistInvalidOperationError) as ex:
                self.runner.run_steps(
                    {
                        "steps": [
                            {
                                "step": {
                                    "action": "EVENTS_CREATE",
                                    "wait_time": 10,
                                    "asset_label": "Nonexistent asset",
                                    "archivist_label": "TestArchivist",
                                },
                                **EVENTS_CREATE,
                            }
                        ],
                    }
                )

            self.assertEqual("unknown asset" in str(ex.exception), True)

    def test_runner_events_create_illegal_location_label(self):
        """
        Test runner operation
        """
        with mock.patch.object(
            self.arch.events, "create_from_data"
        ) as mock_events_create:
            mock_events_create.return_value = Event(**EVENT_RESPONSE)
            with self.assertRaises(ArchivistInvalidOperationError) as ex:
                self.runner.run_steps(
                    {
                        "steps": [
                            {
                                "step": {
                                    "action": "EVENTS_CREATE",
                                    "wait_time": 10,
                                    "location_label": "Nonexistent location",
                                    "archivist_label": "TestArchivist",
                                },
                                **EVENTS_CREATE,
                            }
                        ],
                    }
                )

            self.assertEqual("unknown location" in str(ex.exception), True)

    def test_runner_events_create_location_identity(self):
        """
        Test runner operation
        """
        with mock.patch.object(
            self.arch.events, "create_from_data"
        ) as mock_events_create:
            mock_events_create.return_value = Event(**EVENT_RESPONSE)
            self.runner.run_steps(
                {
                    "steps": [
                        {
                            "step": {
                                "action": "EVENTS_CREATE",
                                "location_label": LOCATION_IDENTITY,
                                "archivist_label": "TestArchivist",
                            },
                            **EVENTS_CREATE,
                        }
                    ],
                }
            )
            mock_events_create.assert_called_once_with(EVENTS_CREATE)

    def test_runner_events_create_location_bad_identity(self):
        """
        Test runner operation
        """
        with mock.patch.object(
            self.arch.events, "create_from_data"
        ) as mock_events_create:
            mock_events_create.return_value = Event(**EVENT_RESPONSE)
            with self.assertRaises(ArchivistInvalidOperationError) as ex:
                self.runner.run_steps(
                    {
                        "steps": [
                            {
                                "step": {
                                    "action": "EVENTS_CREATE",
                                    "location_label": LOCATION_IDENTITY_BAD_UUID,
                                    "archivist_label": "TestArchivist",
                                },
                                **EVENTS_CREATE,
                            }
                        ],
                    }
                )

            self.assertEqual(
                "invalid locations/add30235-xxxx-xxxx-xxxx-d5ef82c4c96f"
                in str(ex.exception),
                True,
            )

    def test_runner_assets_create_invalid_action(self):
        """
        Test runner operation
        """
        with mock.patch.object(
            self.arch.assets, "create_from_data"
        ) as mock_assets_create:
            mock_assets_create.return_value = Asset(**ASSETS_RESPONSE)
            with self.assertRaises(ArchivistInvalidOperationError) as ex:
                self.runner.run_steps(
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

            self.assertEqual("Illegal Action" in str(ex.exception), True)

    @mock.patch("archivist.runner.time_sleep")
    def test_runner_assets_create_invalid_verb_caught(self, mock_sleep):
        """
        Test runner operation
        """
        with mock.patch.object(
            self.arch.assets, "create_from_data"
        ) as mock_assets_create:
            mock_assets_create.return_value = Asset(**ASSETS_RESPONSE)
            self.runner(
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
