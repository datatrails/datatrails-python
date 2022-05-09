"""
Test runner
"""

from os import getenv, environ
from unittest import TestCase

from jinja2 import Environment, FileSystemLoader
from pyaml_env import parse_config
import yaml

# pylint: disable=fixme
# pylint: disable=missing-docstring
# pylint: disable=unused-variable

from archivist import logger
from archivist.runner import Runner

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
        self.runner = Runner()

    def tearDown(self):
        self.runner = None

    def test_runner_dynamic_tolerance(self):
        """
        Test runner with dynamic tolerance story

        uses ARCHIVIST_NAMESPACE to set namespace value

        run_steps is used so that exceptions are shown
        """
        LOGGER.info("...")
        with open(
            "functests/test_resources/dynamic_tolerance_story.yaml",
            "r",
            encoding="utf-8",
        ) as y:
            self.runner.run_steps(parse_config(data=y))
            self.assertEqual(
                len(self.runner.entities),
                2,
                msg="Incorrect number of entities",
            )

    def test_runner_synsation(self):
        """
        Test runner with synsation story

        uses ARCHIVIST_NAMESPACE to set namespace value

        run_steps is used so that exceptions are shown
        """

        LOGGER.info("...")
        jinja = Environment(
            loader=FileSystemLoader("functests/test_resources"),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        template = jinja.get_template("synsation_story.yaml.j2")
        with open(
            "functests/test_resources/synsation_story.values.yaml",
            "r",
            encoding="utf-8",
        ) as fd:
            # render template into yaml which is then converted
            # to a dict....
            self.runner.run_steps(
                yaml.load(
                    template.render(
                        yaml.load(
                            fd,
                            Loader=yaml.SafeLoader,
                        ),
                        env=environ,
                    ),
                    Loader=yaml.SafeLoader,
                ),
            )
            self.assertEqual(
                len(self.runner.entities),
                10,
                msg="Incorrect number of entities",
            )

    def test_runner_richness(self):
        """
        Test runner with richness story

        uses ARCHIVIST_NAMESPACE to set namespace value

        run_steps is used so that exceptions are shown
        """

        LOGGER.info("...")
        with open(
            "functests/test_resources/richness_story.yaml",
            "r",
            encoding="utf-8",
        ) as y:
            self.runner.run_steps(parse_config(data=y))
            self.assertEqual(
                len(self.runner.entities),
                4,
                msg="Incorrect number of entities",
            )

    def test_runner_door_entry(self):
        """
        Test runner with door_entry story

        uses ARCHIVIST_NAMESPACE to set namespace value

        run_steps is used so that exceptions are shown
        """

        LOGGER.info("...")
        with open(
            "functests/test_resources/door_entry_story.yaml",
            "r",
            encoding="utf-8",
        ) as y:
            self.runner.run_steps(parse_config(data=y))
            self.assertEqual(
                len(self.runner.entities),
                12,
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
            self.runner.run_steps(parse_config(data=y))
            self.assertEqual(
                len(self.runner.entities),
                1,
                msg="Incorrect number of entities",
            )

    def test_runner_wipp(self):
        """
        Test runner with wipp story

        uses ARCHIVIST_NAMESPACE to set namespace value

        run_steps is used so that exceptions are shown
        """

        LOGGER.info("...")
        with open(
            "functests/test_resources/wipp_story.yaml",
            "r",
            encoding="utf-8",
        ) as y:
            self.runner.run_steps(parse_config(data=y))
            self.assertEqual(
                len(self.runner.entities),
                3,
                msg="Incorrect number of entities",
            )

    def test_runner_sbom(self):
        """
        Test runner with sbom story

        run_steps is used so that exceptions are shown
        """

        LOGGER.info("...")
        with open(
            "functests/test_resources/sbom_story.yaml",
            "r",
            encoding="utf-8",
        ) as y:
            self.runner.run_steps(parse_config(data=y))
            self.assertEqual(
                len(self.runner.entities),
                2,
                msg="Incorrect number of entities",
            )

    def test_runner_access_policies(self):
        """
        Test runner with access_policies story

        run_steps is used so that exceptions are shown
        """

        LOGGER.info("...")
        with open(
            "functests/test_resources/access_policies_story.yaml",
            "r",
            encoding="utf-8",
        ) as y:
            self.runner.run_steps(parse_config(data=y))
            self.assertGreater(
                len(self.runner.entities),
                0,
                msg="Incorrect number of entities",
            )

    def test_runner_subjects(self):
        """
        Test runner with subjects story

        run_steps is used so that exceptions are shown
        """

        LOGGER.info("...")
        with open(
            "functests/test_resources/subjects_story.yaml",
            "r",
            encoding="utf-8",
        ) as y:
            self.runner.run_steps(parse_config(data=y))
            self.assertGreater(
                len(self.runner.entities),
                0,
                msg="Incorrect number of entities",
            )
