"""Archivist Proof Mechanism

   Enumerated type that allows user to select the proof_mechanism option when
   creating an asset.

"""

# pylint: disable=unused-private-member

from enum import Enum


class ProofMechanism(Enum):
    """Enumerate proof mechanism options"""

    # previously used but now removed
    __RESERVED = 1
    #: Assets and events are proven using a hash of the originator's evidence
    SIMPLE_HASH = 2
