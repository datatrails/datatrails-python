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
from .dictmerge import _deepmerge
from .logger import set_logger
from .utils import get_auth

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
        value = self._enum[values]  # pyright: ignore
        setattr(namespace, self.dest, value)


def simple_parser(description: str):
    """Construct parser with bare minimum features"""
    parser = argparse.ArgumentParser(
        description=description,
    )
    return parser


def common_parser(description: str):
    """Construct parser with security option for token/auth authentication"""
    parser = simple_parser(description)
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
        default="https://app.datatrails.ai",
        help="url of Archivist service",
    )
    parser.add_argument(
        "--auth-token",
        type=str,
        dest="auth_token",
        action="store",
        default=None,
        help="API token value",
    )
    parser.add_argument(
        "--auth-token-filename",
        type=str,
        dest="auth_token_filename",
        action="store",
        default=None,
        help="FILE containing API authentication token",
    )
    parser.add_argument(
        "--client-id",
        type=str,
        dest="client_id",
        action="store",
        default=None,
        help="Client ID from appregistrations",
    )
    parser.add_argument(
        "--client-secret",
        type=str,
        dest="client_secret",
        action="store",
        default=None,
        help="Client secret from appregistrations",
    )
    parser.add_argument(
        "--client-secret-filename",
        type=str,
        dest="client_secret_filename",
        action="store",
        default=None,
        help="FILE containing client secret from appregistrations",
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
    parser.add_argument(
        "-p",
        "--partner_id",
        type=str,
        dest="partner_id",
        action="store",
        default=None,
        help="partner id",
    )

    return parser


def endpoint(args):
    if args.verbose:
        set_logger("DEBUG")
    else:
        set_logger("INFO")

    arch = None
    LOGGER.info("Initializing connection to DATATRAILS...")
    fixtures = {}
    if args.namespace is not None:
        fixtures = _deepmerge(
            fixtures,
            {
                "assets": {
                    "attributes": {
                        "arc_namespace": args.namespace,
                    },
                },
            },
        )

    auth = get_auth(
        auth_token=args.auth_token,
        auth_token_filename=args.auth_token_filename,
        client_id=args.client_id,
        client_secret=args.client_secret,
        client_secret_filename=args.client_secret_filename,
    )

    if auth is None:
        LOGGER.error("Critical error.  Aborting.")
        sys_exit(1)

    arch = Archivist(
        args.url,
        auth,
        fixtures=fixtures,
        partner_id=args.partner_id,
    )
    if arch is None:
        LOGGER.error("Critical error.  Aborting.")
        sys_exit(1)

    return arch
