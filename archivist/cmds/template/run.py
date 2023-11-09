# pylint:  disable=missing-docstring

from logging import getLogger
from os import environ
from pathlib import PurePath
from sys import exit as sys_exit

import yaml
from jinja2 import Environment, FileSystemLoader

from ... import about

# pylint:disable=cyclic-import      # but pylint doesn't understand this feature
from ... import archivist as type_helper  # pylint:disable=unused-import

LOGGER = getLogger(__name__)


def run(arch: "type_helper.Archivist", args):
    LOGGER.info("Using version %s of datatrails-archivist", about.__version__)
    LOGGER.info("Namespace %s", args.namespace)

    path = PurePath(args.template)
    jinja = Environment(
        loader=FileSystemLoader(path.parent),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = jinja.get_template(path.name)

    # if namespace is specified on the commandline then override any environment
    # setting...
    if args.namespace:
        environ["DATATRAILS_UNIQUE_ID"] = args.namespace

    # environment is injected into the template
    with open(args.values, "r", encoding="utf-8") as fd:
        arch.runner(
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

    sys_exit(0)
