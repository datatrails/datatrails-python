# pylint:  disable=missing-docstring

from logging import getLogger
from sys import exit as sys_exit
from sys import stdout as sys_stdout

from archivist.archivist import Archivist
from archivist.cmds.usage.run import run
from archivist.parser import common_parser

LOGGER = getLogger(__name__)


def main():
    parser = common_parser(description="RKVST Diagnostic Tool")

    args = parser.parse_args()

    arch = Archivist(
        args.url,
        (args.client_id, args.client_secret),
    )

    run(arch, args)

    parser.print_help(sys_stdout)
    sys_exit(1)
