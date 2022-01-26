"""uploader interface
"""

from logging import getLogger

import backoff

from .errors import ArchivistNotFoundError


# pylint:disable=unused-import      # To prevent cyclical import errors forward referencing is used
# pylint:disable=cyclic-import      # but pylint doesn't understand this feature
from . import sboms

MAX_TIME = 1200

LOGGER = getLogger(__name__)


def __lookup_max_time():
    return MAX_TIME


# pylint: disable=consider-using-f-string
def __backoff_handler(details):
    LOGGER.debug("MAX_TIME %s", MAX_TIME)
    LOGGER.debug(
        "Backing off {wait:0.1f} seconds afters {tries} tries "
        "calling function {target} with args {args} and kwargs "
        "{kwargs}".format(**details)
    )


def __on_giveup_uploading(details):
    identity = details["args"][1]  # first argument to wait_for_uploading
    elapsed = details["elapsed"]
    raise ArchivistNotFoundError(
        f"uploading for {identity} timed out after {elapsed} seconds"
    )


@backoff.on_predicate(
    backoff.expo,
    logger=None,
    max_time=__lookup_max_time,
    on_backoff=__backoff_handler,
    on_giveup=__on_giveup_uploading,
)
def _wait_for_uploading(self, identity):
    """Return None until identity is found"""
    try:
        LOGGER.debug("Uploader Read %s", identity)
        entity = self.read(identity)
    except ArchivistNotFoundError:
        return None

    return entity
