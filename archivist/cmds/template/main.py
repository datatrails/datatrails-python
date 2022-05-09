# pylint:  disable=missing-docstring

from logging import getLogger
from sys import exit as sys_exit
from sys import stdout as sys_stdout

from ...parser import basic_parser, debug_level

from .run import run

LOGGER = getLogger(__name__)


def main():
    parser = basic_parser("Executes the archivist runner from a template file")

    parser.add_argument(
        "values",
        help="the values file describing the data to be injected into the template",
    )
    parser.add_argument(
        "template", help="the template file describing the operations to conduct"
    )
    args = parser.parse_args()

    debug_level(args)

    run(args)

    parser.print_help(sys_stdout)
    sys_exit(1)
