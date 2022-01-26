"""
Test runner
"""

from os import environ
from unittest import TestCase
import yaml

from archivist.archivist import Archivist

# pylint: disable=fixme
# pylint: disable=missing-docstring
# pylint: disable=unused-variable

from archivist import logger

if "TEST_DEBUG" in environ and environ["TEST_DEBUG"]:
    logger.set_logger(environ["TEST_DEBUG"])

LOGGER = logger.LOGGER


class TestRunner(TestCase):
    """
    Test Archivist Runner
    """

    maxDiff = None

    def setUp(self):
        with open(environ["TEST_AUTHTOKEN_FILENAME"], encoding="utf-8") as fd:
            auth = fd.read().strip()
        self.arch = Archivist(
            environ["TEST_ARCHIVIST"], auth, verify=False, max_time=300
        )

    def tearDown(self):
        self.arch = None

    def test_runner_dynamic_tolerance(self):
        """
        Test runner with dynamic tolerance story

        run_steps is used so that exceptions are shown
        """
        LOGGER.info("...")
        with open(
            "functests/test_resources/dynamic_tolerance_story.yaml",
            "r",
            encoding="utf-8",
        ) as y:
            self.arch.runner.run_steps(yaml.load(y, Loader=yaml.SafeLoader))
            self.assertEqual(
                len(self.arch.runner.entities["COMPLIANCE_POLICIES_CREATE"]),
                1,
                msg="Incorrect number of compliance_policies",
            )
            self.assertEqual(
                len(self.arch.runner.entities["ASSETS_CREATE"]),
                1,
                msg="Incorrect number of assets",
            )

    def test_runner_richness(self):
        """
        Test runner with richness story

        run_steps is used so that exceptions are shown
        """

        LOGGER.info("...")
        with open(
            "functests/test_resources/richness_story.yaml",
            "r",
            encoding="utf-8",
        ) as y:
            self.arch.runner.run_steps(yaml.load(y, Loader=yaml.SafeLoader))
            self.assertEqual(
                len(self.arch.runner.entities["COMPLIANCE_POLICIES_CREATE"]),
                2,
                msg="Incorrect number of compliance_policies",
            )
            self.assertEqual(
                len(self.arch.runner.entities["ASSETS_CREATE"]),
                3,
                msg="Incorrect number of assets",
            )
