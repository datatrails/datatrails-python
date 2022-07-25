"""uploader interface
"""
from __future__ import annotations
from logging import getLogger

import backoff

from .errors import ArchivistNotFoundError
from . import sboms


# pylint:disable=cyclic-import      # but pylint doesn't understand this feature
from .utils import backoff_handler

MAX_TIME = 1200

LOGGER = getLogger(__name__)


def __lookup_max_time():
    return MAX_TIME


def __on_giveup_uploading(details):
    identity = details["args"][1]  # first argument to wait_for_uploading
    elapsed = details["elapsed"]
    raise ArchivistNotFoundError(
        f"uploading for {identity} timed out after {elapsed} seconds"
    )


@backoff.on_predicate(
    backoff.expo,
    logger=None,  # type: ignore
    max_time=__lookup_max_time,
    on_backoff=backoff_handler,
    on_giveup=__on_giveup_uploading,
)
def _wait_for_uploading(self: sboms._SBOMSClient, identity: str) -> sboms.SBOM:
    """Return None until identity is found"""
    try:
        LOGGER.debug("Uploader Read %s", identity)
        entity = self.read(identity)
    except ArchivistNotFoundError:
        return None  # type: ignore

    return entity
