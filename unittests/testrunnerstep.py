"""
Test runner
"""
from logging import getLogger
from os import environ
from unittest import TestCase

from archivist.archivist import Archivist

# pylint: disable=missing-docstring
# pylint: disable=protected-access
# pylint: disable=unused-variable

from archivist.runner import _Step
from archivist.logger import set_logger

ASSET_ID = "assets/yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy"

if "TEST_DEBUG" in environ and environ["TEST_DEBUG"]:
    set_logger(environ["TEST_DEBUG"])

LOGGER = getLogger(__name__)


class TestRunnerStep(TestCase):
    """
    Test Archivist Runner
    """

    maxDiff = None

    @staticmethod
    def asset_id_method(unused_label):
        return ASSET_ID

    def setUp(self):
        self.arch = Archivist("url", "authauthauth")

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
            step.args(self.asset_id_method),
            [],
            msg="Incorrect args",
        )
        # a second time to prove memoization is working.
        self.assertEqual(
            step.args(self.asset_id_method),
            [],
            msg="Incorrect args",
        )

        self.assertEqual(
            step.kwargs(self.asset_id_method, {}),
            {"asset_id": ASSET_ID},
            msg="Incorrect kwargs",
        )
        # a second time to prove memoization is working.
        self.assertEqual(
            step.kwargs(self.asset_id_method, {}),
            {"asset_id": ASSET_ID},
            msg="Incorrect kwargs",
        )

        self.assertEqual(
            step.set_asset_label,
            False,
            msg="Incorrect set_asset_label",
        )
        # a second time to prove memoization is working.
        self.assertEqual(
            step.set_asset_label,
            False,
            msg="Incorrect set_asset_label",
        )

        self.assertEqual(
            step.use_asset_label,
            True,
            msg="Incorrect use_asset_label",
        )
        # a second time to prove memoization is working.
        self.assertEqual(
            step.use_asset_label,
            True,
            msg="Incorrect use_asset_label",
        )

        self.assertEqual(
            step.use_location_label,
            False,
            msg="Incorrect use_location_label",
        )
        # a second time to prove memoization is working.
        self.assertEqual(
            step.use_location_label,
            False,
            msg="Incorrect use_location_label",
        )

        self.assertEqual(
            step.set_location_label,
            False,
            msg="Incorrect set_location_label",
        )
        # a second time to prove memoization is working.
        self.assertEqual(
            step.set_location_label,
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
                "asset_label": "Existing Asset",
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
            step.args(self.asset_id_method),
            [ASSET_ID],
            msg="Incorrect args",
        )
        # a second time to prove memoization is working.
        self.assertEqual(
            step.args(self.asset_id_method),
            [ASSET_ID],
            msg="Incorrect args",
        )

        self.assertEqual(
            step.kwargs(self.asset_id_method, {}),
            {},
            msg="Incorrect kwargs",
        )
        # a second time to prove memoization is working.
        self.assertEqual(
            step.kwargs(self.asset_id_method, {}),
            {},
            msg="Incorrect kwargs",
        )

        self.assertEqual(
            step.set_asset_label,
            False,
            msg="Incorrect set_asset_label",
        )
        # a second time to prove memoization is working.
        self.assertEqual(
            step.set_asset_label,
            False,
            msg="Incorrect set_asset_label",
        )

        self.assertEqual(
            step.use_asset_label,
            True,
            msg="Incorrect use_asset_label",
        )
        # a second time to prove memoization is working.
        self.assertEqual(
            step.use_asset_label,
            True,
            msg="Incorrect use_asset_label",
        )

        self.assertEqual(
            step.use_location_label,
            True,
            msg="Incorrect use_location_label",
        )
        # a second time to prove memoization is working.
        self.assertEqual(
            step.use_location_label,
            True,
            msg="Incorrect use_location_label",
        )
