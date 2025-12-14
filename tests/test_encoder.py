import unittest
import numpy as np
import sys
import os

# Add root project path to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.preprocessing.encoder import DNAEncoder

class TestDNAEncoder(unittest.TestCase):
    def setUp(self):
        self.encoder = DNAEncoder(method='integer', max_length=10)

    def test_basic_encoding(self):
        """Prueba que ACGT se codifique correctamente a [1, 2, 3, 4]"""
        seq = "ACGT"
        encoded = self.encoder.encode(seq)
        expected = np.array([1, 2, 3, 4, 0, 0, 0, 0, 0, 0]) # Padding to 10
        np.testing.assert_array_equal(encoded, expected)

    def test_truncation(self):
        """Prueba que secuencias largas se corten a max_length"""
        long_seq = "ACGT" * 10
        encoded = self.encoder.encode(long_seq)
        self.assertEqual(len(encoded), 10)

    def test_unknown_bases(self):
        """Prueba que bases desconocidas (N o errores) sean 0"""
        seq = "ANX"
        encoded = self.encoder.encode(seq)
        # A->1, N->0, X->0 (default get)
        self.assertEqual(encoded[0], 1)
        self.assertEqual(encoded[1], 0)
        self.assertEqual(encoded[2], 0)

if __name__ == '__main__':
    unittest.main()
