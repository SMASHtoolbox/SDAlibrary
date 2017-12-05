import unittest

import numpy as np
from numpy.testing import assert_array_equal
from scipy import sparse

from sdafile.sda_file import SDAFile
from sdafile.testing import data_path


EXAMPLE_A1 = np.zeros((5, 1), dtype=np.float64)

EXAMPLE_A2 = np.empty((4, 3), dtype=np.complex128)
EXAMPLE_A2.real = 0
EXAMPLE_A2.imag = 1

EXAMPLE_A3 = sparse.eye(5).tocoo()


class TestSDAReference(unittest.TestCase):
    """ Test loading SDAreference.sda """

    def setUp(self):
        self.sda_file = SDAFile(data_path('SDAreference.sda'), 'r')

    def tearDown(self):
        del self.sda_file

    def test_header(self):
        sda_file = self.sda_file
        self.assertEqual(sda_file.FileFormat, 'SDA')
        self.assertEqual(sda_file.FormatVersion, '1.1')
        self.assertEqual(sda_file.Writable, 'yes')
        self.assertEqual(sda_file.Created, '18-Nov-2016 14:08:16')
        self.assertEqual(sda_file.Updated, '18-Nov-2016 14:08:17')

    def test_ReferenceArchivedotm(self):
        label = 'ReferenceArchive.m'
        with open(data_path('ReferenceArchive.m'), 'rb') as f:
            contents = f.read()
        self.assertScalar(label, contents)

    def test_example_A1(self):
        """ 5x1 zeros """
        label = 'example A1'
        self.assertArray(label, EXAMPLE_A1)

    def test_example_A2(self):
        """ 4x3 imaginary numbers """
        label = 'example A2'
        self.assertArray(label, EXAMPLE_A2)

    def test_example_A3(self):
        """ 5x5 sparse matrix """
        label = 'example A3'
        extracted = self.sda_file.extract(label)
        self.assertIsInstance(extracted, sparse.coo_matrix)
        assert_array_equal(extracted.toarray(), EXAMPLE_A3.toarray())

    def test_example_A4(self):
        """ Empty array """
        label = 'example A4'
        data = self.sda_file.extract(label)
        self.assertTrue(np.isnan(data))

    def test_example_B(self):
        """ Logical scalar """
        label = 'example B'
        self.assertScalar(label, True)

    def test_example_C(self):
        """ Some text """
        label = 'example C'
        expected = 'Here is some text'
        self.assertScalar(label, expected)

    def test_example_D(self):
        """ Handle to the sine function """
        label = "example D"
        self.assertUnsupported(label)

    def test_example_E(self):
        """ Cell array combining examples A1 and A2 """
        label = "example E"
        extracted = self.sda_file.extract(label)
        self.assertIsInstance(extracted, list)
        self.assertEqual(len(extracted), 2)
        assert_array_equal(extracted[0], EXAMPLE_A1)
        assert_array_equal(extracted[1], EXAMPLE_A2)

    def test_example_F(self):
        """ Structure combining examples A1 and A2 """
        label = "example F"
        extracted = self.sda_file.extract(label)
        self.assertIsInstance(extracted, dict)
        self.assertEqual(len(extracted), 2)
        assert_array_equal(extracted['A1'], EXAMPLE_A1)
        assert_array_equal(extracted['A2'], EXAMPLE_A2)

    def test_example_G(self):
        """ Structure array combining examples A1 and A2 (repeated) """
        label = "example G"
        extracted = self.sda_file.extract(label)
        self.assertIsInstance(extracted, np.ndarray)
        self.assertTrue(np.issubdtype(extracted.dtype, np.object_))
        self.assertTrue(extracted.shape, (2, 1))
        el1 = extracted[0, 0]
        self.assertIsInstance(el1, dict)
        self.assertEqual(len(el1), 2)
        assert_array_equal(el1['A1'], EXAMPLE_A1)
        assert_array_equal(el1['A2'], EXAMPLE_A2)
        el2 = extracted[1, 0]
        self.assertIsInstance(el2, dict)
        self.assertEqual(len(el2), 2)
        assert_array_equal(el2['A1'], EXAMPLE_A1)
        assert_array_equal(el2['A2'], EXAMPLE_A2)

    def test_example_H(self):
        """ Cell array of structures combining examples A1-A4 """
        label = "example H"
        extracted = self.sda_file.extract(label)
        self.assertIsInstance(extracted, np.ndarray)
        self.assertTrue(np.issubdtype(extracted.dtype, np.object_))
        self.assertTrue(extracted.shape, (2, 1))
        el1 = extracted[0, 0]
        self.assertIsInstance(el1, dict)
        self.assertEqual(len(el1), 2)
        assert_array_equal(el1['A1'], EXAMPLE_A1)
        assert_array_equal(el1['A2'], EXAMPLE_A2)
        el2 = extracted[1, 0]
        self.assertIsInstance(el2, dict)
        self.assertEqual(len(el2), 2)
        assert_array_equal(el2['A3'].toarray(), EXAMPLE_A3.toarray())
        self.assertTrue(np.isnan(el2['A4']))

    def test_example_I(self):
        """ Object containing example A1 """
        label = "example I"
        extracted = self.sda_file.extract(label)
        self.assertIsInstance(extracted, dict)
        self.assertEqual(len(extracted), 1)
        assert_array_equal(extracted['Parameter'], EXAMPLE_A1)

    def test_example_J(self):
        """ Object array containing examples A1 and A2 """
        label = "example J"
        extracted = self.sda_file.extract(label)
        self.assertIsInstance(extracted, np.ndarray)
        self.assertTrue(np.issubdtype(extracted.dtype, np.object_))
        self.assertTrue(extracted.shape, (2, 1))
        el1 = extracted[0, 0]
        self.assertIsInstance(el1, dict)
        self.assertEqual(len(el1), 1)
        assert_array_equal(el1['Parameter'], EXAMPLE_A1)
        el2 = extracted[1, 0]
        self.assertIsInstance(el2, dict)
        self.assertEqual(len(el2), 1)
        assert_array_equal(el2['Parameter'], EXAMPLE_A2)

    def assertArray(self, label, expected):
        extracted = self.sda_file.extract(label)
        self.assertEqual(extracted.dtype, expected.dtype)
        assert_array_equal(extracted, expected)

    def assertScalar(self, label, expected):
        extracted = self.sda_file.extract(label)
        self.assertEqual(extracted, expected)

    def assertUnsupported(self, label):
        with self.assertRaises(ValueError):
            self.sda_file.extract(label)
