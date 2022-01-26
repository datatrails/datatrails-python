"""withdrawer interface

   Wrap base methods with constants for assets (path, etc...
"""

from logging import getLogger

import backoff

from .errors import ArchivistUnwithdrawnError


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


def __on_giveup_withdrawn(details):
    identity = details["args"][1]
    elapsed = details["elapsed"]
    raise ArchivistUnwithdrawnError(
        f"withdrawn for {identity} timed out after {elapsed} seconds"
    )


@backoff.on_predicate(
    backoff.expo,
    logger=None,
    max_time=__lookup_max_time,
    on_backoff=__backoff_handler,
    on_giveup=__on_giveup_withdrawn,
)
def _wait_for_withdrawn(self, identity):
    """Return None until withdrawn date is set"""
    entity = self.read(identity)

    if entity.withdrawn_date:
        return entity

    return None
