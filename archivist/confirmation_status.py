"""Archivist Confirmation Status

   Enumerated type that allows user to select the confirmation status option when
   creating an asset.

"""

# pylint: disable=unused-private-member

from enum import Enum


class ConfirmationStatus(Enum):
    """Enumerate confirmation status options"""

    UNSPECIFIED = 0
    # not yet committed
    PENDING = 1
    CONFIRMED = 2
    # permanent failure
    FAILED = 3
    # forestrie, "its in the db"
    STORED = 4
    # forestrie, "you can know if its changed"
    COMMITTED = 5
    # forestrie, "You easily prove it was publicly available to all"
    UNEQUIVOCAL = 6
