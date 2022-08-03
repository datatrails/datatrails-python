# pylint:  disable=missing-docstring

from logging import getLogger
from os import environ
from sys import exit as sys_exit
from warnings import filterwarnings

from pyaml_env import parse_config

from archivist import about
from archivist.archivist import Archivist

filterwarnings("ignore", message="Unverified HTTPS request")


LOGGER = getLogger(__name__)


def run(arch: Archivist, args):

    LOGGER.info("Using version %s of jitsuin-archivist", about.__version__)
    LOGGER.info("Namespace %s", args.namespace)

    # if namespace is specified on the commandline then override any environment
    # setting...
    if args.namespace:
        environ["ARCHIVIST_NAMESPACE"] = args.namespace

    with open(args.yamlfile, "r", encoding="utf-8") as y:
        arch.runner(parse_config(data=y))

    sys_exit(0)
