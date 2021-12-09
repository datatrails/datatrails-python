"""publisher interface

   Wrap base methods with constants for assets (path, etc...
"""

import logging

from typing import overload

import backoff

from .errors import ArchivistUnpublishedError


# pylint:disable=unused-import      # To prevent cyclical import errors forward referencing is used
# pylint:disable=cyclic-import      # but pylint doesn't understand this feature
from . import sboms

MAX_TIME = 1200

LOGGER = logging.getLogger(__name__)


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


def __on_giveup_publication(details):
    identity = details["args"][1]
    elapsed = details["elapsed"]
    raise ArchivistUnpublishedError(
        f"publication for {identity} timed out after {elapsed} seconds"
    )


# These overloads are used for type hinting, if self is sboms client then
# an SBOM metadata will be returned.
# Overloads are evaluated at startup but not at runtime, therefore
# no test coverage be done directly.


@overload
def _wait_for_publication(
    self: "sboms._SbomsClient", identity: str
) -> "sbommetadata.SBOM":
    ...  # pragma: no cover


@backoff.on_predicate(
    backoff.expo,
    logger=LOGGER,
    max_time=__lookup_max_time,
    on_backoff=__backoff_handler,
    on_giveup=__on_giveup_publication,
)
def _wait_for_publication(self, identity):
    """docstring"""
    entity = self.read(identity)

    if entity.published_date:
        return entity

    return None
