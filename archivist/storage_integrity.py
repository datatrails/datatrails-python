"""Archivist Storage integrity

   Enumerated type that allows user to select the storage option when
   creating an asset.

"""

from enum import Enum


class StorageIntegrity(Enum):
    """Enumerate storage integrity options"""

    #: Assets are stored on the DLT
    LEDGER = 1
    #: Assets are not stored on the DLT
    TENANT_STORAGE = 2
