# pylint:  disable=missing-docstring

from logging import getLogger
from os import environ
from sys import exit as sys_exit

from ... import about

# pylint:disable=cyclic-import      # but pylint doesn't understand this feature
from ... import archivist as type_helper  # pylint:disable=unused-import


LOGGER = getLogger(__name__)


def run(arch, args):
    """Run diagnostic script."""
    LOGGER.info("Using version %s of jitsuin-archivist", about.__version__)
    LOGGER.info("Namespace %s", args.namespace)

    # if namespace is specified on the commandline then override any environment
    # setting...
    if args.namespace:
        environ["ARCHIVIST_NAMESPACE"] = args.namespace

    arch.usage()

    sys_exit(0)
