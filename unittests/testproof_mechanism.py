"""
Test proof mechanism
"""

# pylint: disable=attribute-defined-outside-init
# pylint: disable=missing-docstring
# pylint: disable=too-few-public-methods

from unittest import TestCase

from archivist.proof_mechanism import ProofMechanism


class TestProofMechanism(TestCase):
    """
    Test proof mechanism for archivist
    """

    def test_proof_mechanism(self):
        """
        Test proof_mechanism
        """
        self.assertEqual(ProofMechanism.KHIPU.value, 1, msg="Incorrect value")
        self.assertEqual(ProofMechanism.KHIPU.name, "KHIPU", msg="Incorrect value")
        self.assertEqual(ProofMechanism.SIMPLE_HASH.value, 2, msg="Incorrect value")
        self.assertEqual(
            ProofMechanism.SIMPLE_HASH.name,
            "SIMPLE_HASH",
            msg="Incorrect value",
        )
