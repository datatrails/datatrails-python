"""assets interface

   Wrap base methods with constants for assets (path, etc...
"""

from copy import deepcopy

import backoff

from .constants import (
    CONFIRMATION_CONFIRMED,
    CONFIRMATION_FAILED,
    CONFIRMATION_PENDING,
    CONFIRMATION_STATUS,
)
from .errors import ArchivistUnconfirmedError
from .logger import LOGGER

MAX_TIME = 1200


def __lookup_max_time():
    return MAX_TIME


def __backoff_handler(details):
    LOGGER.debug("MAX_TIME %s", MAX_TIME)
    LOGGER.debug(
        "Backing off {wait:0.1f} seconds afters {tries} tries "
        "calling function {target} with args {args} and kwargs "
        "{kwargs}".format(**details)
    )


def __on_giveup_confirmation(details):
    identity = details["args"][1]
    elapsed = details["elapsed"]
    raise ArchivistUnconfirmedError(
        f"confirmation for {identity} timed out after {elapsed} seconds"
    )


@backoff.on_predicate(
    backoff.expo,
    logger=LOGGER,
    max_time=__lookup_max_time,
    on_backoff=__backoff_handler,
    on_giveup=__on_giveup_confirmation,
)
def wait_for_confirmation(self, identity):
    """docstring"""
    entity = self.read(identity)

    if CONFIRMATION_STATUS not in entity:
        raise ArchivistUnconfirmedError(
            f"cannot confirm {identity} as confirmation_status is not present"
        )

    if entity[CONFIRMATION_STATUS] == CONFIRMATION_FAILED:
        raise ArchivistUnconfirmedError(
            f"confirmation for {identity} FAILED - this is unusable"
        )

    if entity[CONFIRMATION_STATUS] == CONFIRMATION_CONFIRMED:
        return entity

    return None


def __on_giveup_confirmed(details):
    self = details["args"][0]
    count = self.pending_count
    elapsed = details["elapsed"]
    raise ArchivistUnconfirmedError(
        f"{count} pending assets still present after {elapsed} seconds"
    )


@backoff.on_predicate(
    backoff.expo,
    logger=LOGGER,
    max_time=__lookup_max_time,
    on_backoff=__backoff_handler,
    on_giveup=__on_giveup_confirmed,
)
def wait_for_confirmed(self, *, props=None, **kwargs):
    """docstring"""
    newprops = deepcopy(props) if props else {}
    newprops[CONFIRMATION_STATUS] = CONFIRMATION_PENDING

    LOGGER.debug("Count unconfirmed assets %s", newprops)
    count = self.count(props=newprops, **kwargs)

    if count == 0:
        # did any fail
        newprops = deepcopy(props) if props else {}
        newprops[CONFIRMATION_STATUS] = CONFIRMATION_FAILED
        count = self.count(props=newprops, **kwargs)
        if count > 0:
            raise ArchivistUnconfirmedError(f"There are {count} FAILED assets")

        return True

    self.pending_count = count
    return False
