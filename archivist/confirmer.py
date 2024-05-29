"""assets confirmer interface
"""

from copy import deepcopy
from logging import getLogger
from typing import TYPE_CHECKING, Any, Union, overload

import backoff

if TYPE_CHECKING:
    # pylint:disable=cyclic-import      # but pylint doesn't understand this feature
    from backoff._typing import Details

    from .assets import Asset, _AssetsPublic, _AssetsRestricted
    from .events import Event, _EventsPublic, _EventsRestricted


from .confirmation_status import ConfirmationStatus
from .constants import CONFIRMATION_STATUS
from .errors import ArchivistUnconfirmedError
from .utils import backoff_handler

MAX_TIME = 300
LOGGER = getLogger(__name__)

# pylint: disable=protected-access
PublicManagers = Union["_AssetsPublic", "_EventsPublic"]
PrivateManagers = Union["_AssetsRestricted", "_EventsRestricted"]
Managers = Union[PublicManagers, PrivateManagers]
ReturnTypes = Union["Asset", "Event"]


def __lookup_max_time():
    return MAX_TIME


def __on_giveup_confirmation(details: "Details"):
    identity: str = details["args"][1]
    elapsed: float = details["elapsed"]
    raise ArchivistUnconfirmedError(
        f"confirmation for {identity} timed out after {elapsed} seconds"
    )


# These overloads are used for type hinting, if self is events client then
# an event will be returned. If self is Asset client then an asset will be
# returned. Overloads are evaluated at startup but not at runtime, therefore
# no test coverage be done directly.


@overload
def _wait_for_confirmation(
    self: "_AssetsRestricted",
    identity: str,
) -> "Asset": ...  # pragma: no cover


@overload
def _wait_for_confirmation(
    self: "_AssetsPublic",
    identity: str,
) -> "Asset": ...  # pragma: no cover


@overload
def _wait_for_confirmation(
    self: "_EventsRestricted",
    identity: str,
) -> "Event": ...  # pragma: no cover


@overload
def _wait_for_confirmation(
    self: "_EventsPublic",
    identity: str,
) -> "Event": ...  # pragma: no cover


@backoff.on_predicate(
    backoff.expo,
    max_value=30.0,
    logger=None,  # pyright: ignore
    max_time=__lookup_max_time,
    on_backoff=backoff_handler,
    on_giveup=__on_giveup_confirmation,
)
def _wait_for_confirmation(self: Managers, identity: str) -> ReturnTypes:
    """Return None until entity is confirmed"""

    entity = self.read(identity)

    LOGGER.debug("entity %s", entity)
    if CONFIRMATION_STATUS not in entity:
        raise ArchivistUnconfirmedError(
            f"cannot confirm {identity} as confirmation_status is not present"
        )

    status = entity[CONFIRMATION_STATUS]
    if status == ConfirmationStatus.FAILED.name:
        raise ArchivistUnconfirmedError(
            f"confirmation for {identity} FAILED - this is unusable"
        )

    if status in (
        ConfirmationStatus.CONFIRMED.name,
        ConfirmationStatus.COMMITTED.name,
        ConfirmationStatus.UNEQUIVOCAL.name,
    ):
        return entity

    return None  # pyright: ignore


def __on_giveup_confirmed(details: "Details"):
    self: PrivateManagers = details["args"][0]
    count = self.pending_count
    elapsed: float = details["elapsed"]
    raise ArchivistUnconfirmedError(
        f"{count} pending assets still present after {elapsed} seconds"
    )


@backoff.on_predicate(
    backoff.expo,
    max_value=30.0,
    logger=None,  # pyright: ignore
    max_time=__lookup_max_time,
    on_backoff=backoff_handler,
    on_giveup=__on_giveup_confirmed,
)
def _wait_for_confirmed(
    self: PrivateManagers,
    *,
    props: "dict[str, Any]|None" = None,
    **kwargs: Any,
) -> bool:
    """Return False until all entities are confirmed"""

    # look for pending entities
    newprops = deepcopy(props) if props else {}
    newprops[CONFIRMATION_STATUS] = ConfirmationStatus.PENDING.name
    LOGGER.debug("Count pending entities %s", newprops)
    pending_count = self.count(props=newprops, **kwargs)

    # look for stored entities
    newprops = deepcopy(props) if props else {}
    newprops[CONFIRMATION_STATUS] = ConfirmationStatus.STORED.name
    LOGGER.debug("Count stored entities %s", newprops)
    stored_count = self.count(props=newprops, **kwargs)

    count = pending_count + stored_count

    if count == 0:
        # did any fail
        newprops = deepcopy(props) if props else {}
        newprops[CONFIRMATION_STATUS] = ConfirmationStatus.FAILED.name
        count = self.count(props=newprops, **kwargs)
        if count > 0:
            raise ArchivistUnconfirmedError(f"There are {count} FAILED entities")

        return True

    self.pending_count = count
    return False
