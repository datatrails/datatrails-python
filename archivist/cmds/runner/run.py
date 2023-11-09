# pylint:  disable=missing-docstring


from logging import getLogger
from os import environ
from sys import exit as sys_exit
from typing import TYPE_CHECKING

from pyaml_env import parse_config

# pylint:disable=cyclic-import      # but pylint doesn't understand this feature
from ... import about

if TYPE_CHECKING:
    from ...archivist import Archivist

LOGGER = getLogger(__name__)


def run(arch: "Archivist", args):
    LOGGER.info("Using version %s of datatrails-archivist", about.__version__)
    LOGGER.info("Namespace %s", args.namespace)

    # if namespace is specified on the commandline then override any environment
    # setting...
    if args.namespace:
        environ["DATATRAILS_UNIQUE_ID"] = args.namespace

    with open(args.yamlfile, "r", encoding="utf-8") as yml:
        arch.runner(parse_config(data=yml))

    sys_exit(0)
