"""
Test proof mechanism
"""

# pylint: disable=protected-access

from unittest import TestCase

from archivist.proof_mechanism import ProofMechanism


class TestProofMechanism(TestCase):
    """
    Test proof mechanism for archivist
    """

    def test_proof_mechanism_simple_hash(self):
        """
        Test proof_mechanism
        """
        self.assertEqual(ProofMechanism.SIMPLE_HASH.value, 2, msg="Incorrect value")

        self.assertEqual(
            ProofMechanism.SIMPLE_HASH.name,
            "SIMPLE_HASH",
            msg="Incorrect value",
        )

    def test_proof_mechanism_metkle_log(self):
        """
        Test proof_mechanism
        """
        self.assertEqual(ProofMechanism.MERKLE_LOG.value, 3, msg="Incorrect value")

        self.assertEqual(
            ProofMechanism.MERKLE_LOG.name,
            "MERKLE_LOG",
            msg="Incorrect value",
        )

    def test_proof_mechanism_reserved(self):
        """
        Test proof_mechanism
        """
        with self.assertRaises(AttributeError):
            self.assertEqual(ProofMechanism.__RESERVED.value, 1, msg="Incorrect value")

        with self.assertRaises(AttributeError):
            self.assertEqual(
                ProofMechanism.__RESERVED.name, "__RESERVED", msg="Incorrect value"
            )
