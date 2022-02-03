"""common parser argument
"""

# pylint:  disable=missing-docstring
# pylint:  disable=too-few-public-methods


import argparse
from enum import Enum
from logging import getLogger
from sys import exit as sys_exit
from warnings import filterwarnings

from .archivist import Archivist
from .logger import set_logger
from .dictmerge import _deepmerge
from .proof_mechanism import ProofMechanism


filterwarnings("ignore", message="Unverified HTTPS request")


LOGGER = getLogger(__name__)


# from https://stackoverflow.com/questions/43968006/support-for-enum-arguments-in-argparse
class EnumAction(argparse.Action):
    """
    Argparse action for handling Enums
    """

    def __init__(self, **kwargs):
        # Pop off the type value
        enum_type = kwargs.pop("type", None)

        # Ensure an Enum subclass is provided
        if enum_type is None:
            raise ValueError("type must be assigned an Enum when using EnumAction")

        if not issubclass(enum_type, Enum):
            raise TypeError("type must be an Enum when using EnumAction")

        # Generate choices from the Enum
        kwargs.setdefault("choices", tuple(e.name for e in enum_type))

        super().__init__(**kwargs)

        self._enum = enum_type

    def __call__(self, parser, namespace, values, option_string=None):
        # Convert value back into an Enum
        value = self._enum[values]
        setattr(namespace, self.dest, value)


def common_parser(description: str):
    """Construct parser with security option for token/auth authentication"""
    parser = argparse.ArgumentParser(
        description=description,
    )
    parser.add_argument(
        "-v",
        "--verbose",
        dest="verbose",
        action="store_true",
        default=False,
        help="print verbose debugging",
    )
    parser.add_argument(
        "-u",
        "--url",
        type=str,
        dest="url",
        action="store",
        default="https://rkvst.poc.jitsuin.io",
        help="location of Archivist service",
    )
    parser.add_argument(
        "-p",
        "--proof-mechanism",
        type=ProofMechanism,
        action=EnumAction,
        dest="proof_mechanism",
        default=ProofMechanism.SIMPLE_HASH,
        help="mechanism for proving the evidence for events on the Asset",
    )
    parser.add_argument(
        "-t",
        "--auth-token",
        type=str,
        dest="auth_token_file",
        action="store",
        default=".auth_token",
        required=True,
        help="FILE containing API authentication token",
    )
    parser.add_argument(
        "-n",
        "--namespace",
        type=str,
        dest="namespace",
        action="store",
        default=None,
        help="namespace of item population",
    )

    return parser


def endpoint(args):

    if args.verbose:
        set_logger("DEBUG")
    else:
        set_logger("INFO")

    arch = None
    LOGGER.info("Initialising connection to Jitsuin Archivist...")
    fixtures = {
        "assets": {
            "proof_mechanism": args.proof_mechanism.name,
        },
    }
    if args.namespace is not None:
        fixtures = _deepmerge(
            fixtures,
            {
                "assets": {
                    "attributes": {
                        "arc_namespace": args.namespace,
                    },
                },
                "locations": {
                    "attributes": {
                        "arc_namespace": args.namespace,
                    },
                },
            },
        )

    if args.auth_token_file:
        with open(args.auth_token_file, mode="r", encoding="utf-8") as tokenfile:
            authtoken = tokenfile.read().strip()

        arch = Archivist(args.url, authtoken, verify=False, fixtures=fixtures)

    if arch is None:
        LOGGER.error("Critical error.  Aborting.")
        sys_exit(1)

    return arch
