"""assets confirmer interface
"""


from logging import getLogger
from typing import TYPE_CHECKING

import backoff

if TYPE_CHECKING:
    from .subjects import Subject, _SubjectsClient

from .constants import (
    CONFIRMATION_CONFIRMED,
    CONFIRMATION_STATUS,
)
from .errors import ArchivistUnconfirmedError

# pylint:disable=cyclic-import      # but pylint doesn't understand this feature
from .utils import backoff_handler

MAX_TIME = 1200

LOGGER = getLogger(__name__)


def __lookup_max_time():
    return MAX_TIME


def __on_giveup_confirmation(details):
    identity = details["args"][1]
    elapsed = details["elapsed"]
    raise ArchivistUnconfirmedError(
        f"confirmation for {identity} timed out after {elapsed} seconds"
    )


@backoff.on_predicate(
    backoff.expo,
    logger=None,  # pyright: ignore
    max_time=__lookup_max_time,
    on_backoff=backoff_handler,
    on_giveup=__on_giveup_confirmation,
)
def _wait_for_confirmation(self: "_SubjectsClient", identity: str) -> "Subject":
    """Return None until subjects is confirmed"""
    subject = self.read(identity)
    if CONFIRMATION_STATUS not in subject:
        return None  # pyright: ignore

    if subject[CONFIRMATION_STATUS] == CONFIRMATION_CONFIRMED:
        return subject

    return None  # pyright: ignore
