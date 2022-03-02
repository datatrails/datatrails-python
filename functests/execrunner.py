"""
Test runner
"""

from os import getenv
from unittest import TestCase

from pyaml_env import parse_config

from archivist.archivist import Archivist
from archivist.utils import get_auth

# pylint: disable=fixme
# pylint: disable=missing-docstring
# pylint: disable=unused-variable

from archivist import logger

if getenv("TEST_DEBUG") is not None:
    logger.set_logger(getenv("TEST_DEBUG"))
else:
    logger.set_logger("INFO")

LOGGER = logger.LOGGER


class TestRunner(TestCase):
    """
    Test Archivist Runner
    """

    maxDiff = None

    def setUp(self):
        auth = get_auth(
            auth_token_filename=getenv("TEST_AUTHTOKEN_FILENAME"),
            client_id=getenv("TEST_CLIENT_ID"),
            client_secret_filename=getenv("TEST_CLIENT_SECRET_FILENAME"),
        )
        self.arch = Archivist(
            getenv("TEST_ARCHIVIST"), auth, verify=False, max_time=300
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
            self.arch.runner.run_steps(parse_config(data=y))
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
            self.arch.runner.run_steps(parse_config(data=y))
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
            self.arch.runner.run_steps(parse_config(data=y))
            self.assertEqual(
                len(self.arch.runner.entities),
                11,
                msg="Incorrect number of entities",
            )

    def test_runner_estate_info(self):
        """
        Test runner with estate_info story
        run_steps is used so that exceptions are shown
        """

        LOGGER.info("...")
        with open(
            "functests/test_resources/estate_info_story.yaml",
            "r",
            encoding="utf-8",
        ) as y:
            self.arch.runner.run_steps(parse_config(data=y))

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
            self.arch.runner.run_steps(parse_config(data=y))
            self.assertEqual(
                len(self.arch.runner.entities),
                2,
                msg="Incorrect number of entities",
            )
