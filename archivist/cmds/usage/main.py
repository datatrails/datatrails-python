# pylint:  disable=missing-docstring

from logging import getLogger
from sys import exit as sys_exit
from sys import stdout as sys_stdout

from archivist.cmds.usage.run import run
from archivist.parser import common_parser, endpoint

LOGGER = getLogger(__name__)


def main():
    parser = common_parser(description="RKVST Diagnostic Tool")

    args = parser.parse_args()

    arch = endpoint(args)

    run(arch, args)

    parser.print_help(sys_stdout)
    sys_exit(1)
