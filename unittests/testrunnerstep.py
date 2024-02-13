"""
Test runner step
"""

from logging import getLogger
from os import environ
from unittest import TestCase

from archivist.archivist import Archivist
from archivist.logger import set_logger

# pylint: disable=missing-docstring
# pylint: disable=protected-access
# pylint: disable=unused-variable
from archivist.runner import _Step

ASSET_ID = "assets/yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy"
LOCATION_ID = "locations/yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy"

if "DATATRAILS_LOGLEVEL" in environ and environ["DATATRAILS_LOGLEVEL"]:
    set_logger(environ["DATATRAILS_LOGLEVEL"])

LOGGER = getLogger(__name__)


class TestRunnerStep(TestCase):
    """
    Test Archivist Runner
    """

    maxDiff = None

    @staticmethod
    def asset_id_method(unused_label):
        return ASSET_ID

    @staticmethod
    def location_id_method(unused_label):
        return LOCATION_ID

    def setUp(self):
        self.arch = Archivist("url", "authauthauth")

    def tearDown(self):
        self.arch.close()

    def test_runner_step_with_delete_method(self):
        """
        Test runner step
        """
        step = _Step(
            self.arch,
            **{
                "action": "COMPLIANCE_POLICIES_CREATE",
                "wait_time": 10,
                "print_response": True,
                "description": "Testing runner events list",
                "asset_label": "Existing Asset",
                "delete": True,
            }
        )
        self.assertEqual(
            step.action,
            self.arch.compliance_policies.create_from_data,
            msg="Incorrect action",
        )
        # a second time to prove memoization is working.
        self.assertEqual(
            step.action,
            self.arch.compliance_policies.create_from_data,
            msg="Incorrect action",
        )

        self.assertEqual(
            step.delete_method,
            self.arch.compliance_policies.delete,
            msg="Incorrect delete_method",
        )
        # a second time to prove memoization is working.
        self.assertEqual(
            step.delete_method,
            self.arch.compliance_policies.delete,
            msg="Incorrect delete_method",
        )

    def test_runner_step(self):
        """
        Test runner step
        """
        step = _Step(
            self.arch,
            **{
                "action": "EVENTS_LIST",
                "wait_time": 10,
                "print_response": True,
                "description": "Testing runner events list",
                "asset_label": "Existing Asset",
                "delete": True,
            }
        )
        self.assertEqual(
            step.action,
            self.arch.events.list,
            msg="Incorrect action",
        )
        # a second time to prove memoization is working.
        self.assertEqual(
            step.action,
            self.arch.events.list,
            msg="Incorrect action",
        )

        self.assertEqual(
            step.delete_method,
            None,
            msg="Incorrect delete_method",
        )
        # a second time to prove memoization is working.
        self.assertEqual(
            step.delete_method,
            None,
            msg="Incorrect delete_method",
        )

        self.assertEqual(
            step.label("set", "asset"),
            False,
            msg="Incorrect set_asset_label",
        )
        # a second time to prove memoization is working.
        self.assertEqual(
            step.label("set", "asset"),
            False,
            msg="Incorrect set_asset_label",
        )

        self.assertEqual(
            step.label("use", "asset"),
            "add_kwarg_asset_identity",
            msg="Incorrect use_asset_label",
        )
        # a second time to prove memoization is working.
        self.assertEqual(
            step.label("use", "asset"),
            "add_kwarg_asset_identity",
            msg="Incorrect use_asset_label",
        )

        self.assertEqual(
            step.label("use", "location"),
            False,
            msg="Incorrect use_location_label",
        )
        # a second time to prove memoization is working.
        self.assertEqual(
            step.label("use", "location"),
            False,
            msg="Incorrect use_location_label",
        )

        self.assertEqual(
            step.label("set", "location"),
            False,
            msg="Incorrect set_location_label",
        )
        # a second time to prove memoization is working.
        self.assertEqual(
            step.label("set", "location"),
            False,
            msg="Incorrect set_location_label",
        )

    def test_runner_step_location_label(self):
        """
        Test runner step
        """
        step = _Step(
            self.arch,
            **{
                "action": "EVENTS_CREATE",
                "wait_time": 10,
                "print_response": True,
                "description": "Testing runner events list",
                "location_label": "Existing Location",
            }
        )
        self.assertEqual(
            step.action,
            self.arch.events.create_from_data,
            msg="Incorrect action",
        )
        # a second time to prove memoization is working.
        self.assertEqual(
            step.action,
            self.arch.events.create_from_data,
            msg="Incorrect action",
        )

        self.assertEqual(
            step.keywords,
            ("confirm",),
            msg="Incorrect keywords",
        )
        # a second time to prove memoization is working.
        self.assertEqual(
            step.keywords,
            ("confirm",),
            msg="Incorrect keywords",
        )

        self.assertEqual(
            step.delete_method,
            None,
            msg="Incorrect delete_method",
        )
        # a second time to prove memoization is working.
        self.assertEqual(
            step.delete_method,
            None,
            msg="Incorrect delete_method",
        )

        self.assertEqual(
            step.label("set", "asset"),
            False,
            msg="Incorrect set_asset_label",
        )
        # a second time to prove memoization is working.
        self.assertEqual(
            step.label("set", "asset"),
            False,
            msg="Incorrect set_asset_label",
        )

        self.assertEqual(
            step.label("use", "asset"),
            "add_arg_identity",
            msg="Incorrect use_asset_label",
        )
        # a second time to prove memoization is working.
        self.assertEqual(
            step.label("use", "asset"),
            "add_arg_identity",
            msg="Incorrect use_asset_label",
        )

        self.assertEqual(
            step.label("use", "location"),
            "add_data_location_identity",
            msg="Incorrect use_location_label",
        )
        # a second time to prove memoization is working.
        self.assertEqual(
            step.label("use", "location"),
            "add_data_location_identity",
            msg="Incorrect use_location_label",
        )
