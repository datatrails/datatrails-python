"""publisher interface

   Wrap base methods with constants for assets (path, etc...
"""

from __future__ import annotations
from logging import getLogger

import backoff

from .utils import backoff_handler
from .errors import ArchivistUnpublishedError
from . import sboms


# pylint:disable=cyclic-import      # but pylint doesn't understand this feature

MAX_TIME = 1200

LOGGER = getLogger(__name__)


def __lookup_max_time():
    return MAX_TIME


def __on_giveup_publication(details):
    identity = details["args"][1]
    elapsed = details["elapsed"]
    raise ArchivistUnpublishedError(
        f"publication for {identity} timed out after {elapsed} seconds"
    )


@backoff.on_predicate(
    backoff.expo,
    logger=None,  # type: ignore
    max_time=__lookup_max_time,
    on_backoff=backoff_handler,
    on_giveup=__on_giveup_publication,
)
def _wait_for_publication(self: sboms._SBOMSClient, identity: str) -> sboms.SBOM:
    """Return None until published date is set"""
    entity = self.read(identity)

    if entity.published_date:
        return entity

    return None  # type: ignore
