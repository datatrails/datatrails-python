# pylint:  disable=missing-docstring

from logging import getLogger
from sys import exit as sys_exit
import yaml

from ... import about

# pylint:disable=unused-import      # To prevent cyclical import errors forward referencing is used
# pylint:disable=cyclic-import      # but pylint doesn't understand this feature
from ... import archivist as type_helper


LOGGER = getLogger(__name__)


def run(arch: "type_helper.Archivist", args):

    LOGGER.info("Using version %s of jitsuin-archivist", about.__version__)
    LOGGER.info("Namespace %s", args.namespace)

    with open(args.yamlfile, "r", encoding="utf-8") as y:
        arch.runner(yaml.load(y, Loader=yaml.SafeLoader))

    sys_exit(0)
