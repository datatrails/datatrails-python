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
else:
    logger.set_logger("INFO")

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
                len(self.arch.runner.entities),
                2,
                msg="Incorrect number of entities",
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
                len(self.arch.runner.entities),
                5,
                msg="Incorrect number of entities",
            )

    def test_runner_door_entry(self):
        """
        Test runner with door_entry story

        run_steps is used so that exceptions are shown
        """

        LOGGER.info("...")
        with open(
            "functests/test_resources/door_entry_story.yaml",
            "r",
            encoding="utf-8",
        ) as y:
            self.arch.runner.run_steps(yaml.load(y, Loader=yaml.SafeLoader))
            self.assertEqual(
                len(self.arch.runner.entities),
                11,
                msg="Incorrect number of entities",
            )

    def test_runner_wipp(self):
        """
        Test runner with wipp story

        run_steps is used so that exceptions are shown
        """

        LOGGER.info("...")
        with open(
            "functests/test_resources/wipp_story.yaml",
            "r",
            encoding="utf-8",
        ) as y:
            self.arch.runner.run_steps(yaml.load(y, Loader=yaml.SafeLoader))
            self.assertEqual(
                len(self.arch.runner.entities),
                2,
                msg="Incorrect number of entities",
            )
