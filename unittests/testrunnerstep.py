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

    def setUp(self):
        self.arch = Archivist("url", "authauthauth")

    def tearDown(self):
        self.arch.close()

    def test_runner_step_no_kwargs(self):
        """
        Test runner step
        """

        # this action has no keywords and thsi will test the
        # keywords is not None clause
        steps = {
            "action": "ASSETS_ATTACHMENT_INFO",
        }
        step = _Step(
            self.arch,
            **steps,
        )
        self.assertEqual(
            step.args,
            [],
            msg="Incorrect args",
        )

        def identity_method(_unused):
            return "identity"

        step.init_args(identity_method, steps)
        self.assertEqual(
            step.args,
            [
                steps,
            ],
            msg="Incorrect args",
        )

    def test_runner_step(self):
        """
        Test runner step
        """
        steps = {
            "action": "EVENTS_LIST",
            "wait_time": 10,
            "print_response": True,
            "description": "Testing runner events list",
            "asset_label": "Existing Asset",
            "delete": True,
        }
        step = _Step(
            self.arch,
            **steps,
        )
        self.assertEqual(
            step.args,
            [],
            msg="Incorrect args",
        )

        def identity_method(_unused):
            return "identity"

        step.init_args(identity_method, step)
        self.assertEqual(
            step.args,
            [
                steps,
            ],
            msg="Incorrect args",
        )
        step.add_arg_identity("another_identity")
        self.assertEqual(
            step.args,
            [
                steps,
                "another_identity",
            ],
            msg="Incorrect args",
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
