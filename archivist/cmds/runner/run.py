# pylint:  disable=missing-docstring

from __future__ import annotations
from logging import getLogger
from os import environ
from sys import exit as sys_exit

from pyaml_env import parse_config

from ... import about

# pylint:disable=cyclic-import      # but pylint doesn't understand this feature
from ... import archivist


LOGGER = getLogger(__name__)


def run(arch: archivist.Archivist, args):

    LOGGER.info("Using version %s of jitsuin-archivist", about.__version__)
    LOGGER.info("Namespace %s", args.namespace)

    # if namespace is specified on the commandline then override any environment
    # setting...
    if args.namespace:
        environ["ARCHIVIST_NAMESPACE"] = args.namespace

    with open(args.yamlfile, "r", encoding="utf-8") as yml:
        arch.runner(parse_config(data=yml))

    sys_exit(0)
