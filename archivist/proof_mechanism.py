"""Archivist Proof Mechanism

   Enumerated type that allows user to select the proof_mechanism option when
   creating an asset.

   Currently there is only one proof mechanism so this code is here only for
   compatibility.
"""

# pylint: disable=unused-private-member

from enum import Enum


class ProofMechanism(Enum):
    """Enumerate proof mechanism options"""

    # previously used but now removed
    __RESERVED1 = 1
    SIMPLE_HASH = 2
    #: Assets and events are proven using a merkle log hash of the originator's evidence
    MERKLE_LOG = 3
