"""Archivist Proof Mechanism

   Enumerated type that allows user to select the proof_mechanism option when
   creating an asset.

"""

from enum import Enum


class ProofMechanism(Enum):
    """Enumerate proof mechanism options"""

    #: Assets and events are proven using Jitsuin Khipus on the ledger
    KHIPU = 1
    #: Assets and events are proven using a hash of the originator's evidence
    SIMPLE_HASH = 2
