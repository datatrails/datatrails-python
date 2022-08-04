"""Main function to run usage summary script."""

from logging import getLogger

from ...parser import common_parser, endpoint

# from archivist.cmds.usage.run import run
from .run import run

# from archivist.parser import common_parser, endpoint

LOGGER = getLogger(__name__)


def main():
    """Run diagnostic script."""
    parser = common_parser(description="RKVST Diagnostic Tool")

    args = parser.parse_args()

    arch = endpoint(args)

    run(arch, args)
