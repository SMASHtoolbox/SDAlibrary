import unittest

import numpy as np
from numpy.testing import assert_array_equal, assert_equal
from scipy.sparse import coo_matrix

from sdafile.extract import (
    extract_character, extract_complex, extract_file, extract_logical,
    extract_numeric, extract_sparse, extract_sparse_complex,
)


class TestExtract(unittest.TestCase):

    def test_extract_character(self):
        expected = '01'
        stored = np.array([48, 49], np.uint8).reshape(2, -1)
        extracted = extract_character(stored)
        self.assertEqual(extracted, expected)

    def test_extract_complex(self):
        expected = np.arange(6, dtype=np.complex128)
        expected.imag = -1
        stored = np.vstack([expected.real, expected.imag])
        extracted = extract_complex(stored, (1, 6))
        self.assertEqual(expected.dtype, extracted.dtype)
        assert_array_equal(expected, extracted)

        expected = expected.astype(np.complex64)
        stored = stored.astype(np.float32)
        extracted = extract_complex(stored, (1, 6))
        self.assertEqual(expected.dtype, extracted.dtype)
        assert_array_equal(expected, extracted)

        expected_2d = expected.reshape((2, 3), order='F')
        extracted = extract_complex(stored, (2, 3))
        self.assertEqual(expected_2d.dtype, extracted.dtype)
        assert_array_equal(expected_2d, extracted)

    def test_extract_file(self):
        contents = b'01'
        stored = np.array([48, 49], np.uint8).reshape(1, 2)
        extracted = extract_file(stored)
        self.assertEqual(extracted, contents)

    def test_extract_logical(self):
        self.assertEqual(extract_logical(1), True)
        self.assertEqual(extract_logical(0), False)

        expected = np.array([True, False, True, True], dtype=bool)
        stored = np.atleast_2d(expected.view(np.uint8)).T
        extracted = extract_logical(stored)
        self.assertEqual(extracted.dtype, expected.dtype)
        assert_array_equal(extracted, expected)

    def test_extract_numeric(self):
        expected = np.array([1, 1, 321])
        stored = np.atleast_2d(expected).T
        extracted = extract_numeric(stored)
        assert_array_equal(extracted, expected)

        expected = 3.14159
        stored = np.atleast_2d(expected).T
        extracted = extract_numeric(stored)
        assert_equal(extracted, expected)

    def test_extract_sparse(self):
        row = np.array([0, 2])
        col = np.array([1, 2])
        data = np.array([1, 4])

        stored = np.array([row + 1, col + 1, data])  # one-based indexing
        extracted = extract_sparse(stored)
        expected = np.array([
            [0, 1, 0],
            [0, 0, 0],
            [0, 0, 4],
        ])

        self.assertIsInstance(extracted, coo_matrix)
        assert_array_equal(extracted.toarray(), expected)

    def test_extract_sparse_complex(self):
        row = np.array([3, 4, 5, 6])
        col = np.array([0, 1, 1, 4])
        data = row + (1 + 1j) * col

        idx = 5 * row + col + 1
        stored = np.array([idx, data.real, data.imag])
        extracted = extract_sparse_complex(stored, (7, 5))

        expected = np.zeros((7, 5), dtype=np.complex128)
        expected[row, col] = data
        assert_array_equal(extracted.toarray(), expected)
