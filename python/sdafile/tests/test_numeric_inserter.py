import numpy as np
from scipy.sparse import coo_matrix

from sdafile.numeric_inserter import (
    ArrayInserter, ScalarInserter, SparseInserter,
)
from sdafile.testing import InserterTestCase


class NumericInserterTestCase(InserterTestCase):

    def setUp(self):
        InserterTestCase.setUp(self)
        self.grp_attrs = dict(
            RecordType='numeric',
            Empty='no',
        )
        self.ds_attrs = dict(
            RecordType='numeric',
            Empty='no',
            Complex='no',
            Sparse='no',
        )

    def tearDown(self):
        del self.grp_attrs
        del self.ds_attrs
        InserterTestCase.tearDown(self)


class TestNumericInserterArray(NumericInserterTestCase):

    def test_array_inserter_basic(self):
        data = np.array([1, 1, 321])
        expected = np.atleast_2d(data).T
        self.assertSimpleInsert(
            ArrayInserter,
            data,
            self.grp_attrs,
            self.ds_attrs,
            expected
        )

    def test_array_inserter_array_scalar(self):
        data = np.array(np.pi)
        expected = data.reshape(1, 1)
        self.assertSimpleInsert(
            ArrayInserter,
            data,
            self.grp_attrs,
            self.ds_attrs,
            expected,
        )

    def test_array_inserter_empty(self):
        data = np.array([], float)
        self.grp_attrs['Empty'] = self.ds_attrs['Empty'] = 'yes'
        self.assertSimpleInsert(
            ArrayInserter,
            data,
            self.grp_attrs,
            self.ds_attrs,
            expected=None
        )


class TestNumericInserterComplex(NumericInserterTestCase):

    def setUp(self):
        NumericInserterTestCase.setUp(self)
        self.ds_attrs['Complex'] = 'yes'
        self.ds_attrs['ArraySize'] = (1, 1)

    def test_array_inserter_complex_basic(self):
        data = np.array([1, 1, 321]) + 1j
        self.ds_attrs['ArraySize'] = (1, 3)
        expected = np.array([data.real, data.imag])
        self.assertSimpleInsert(
            ArrayInserter,
            data,
            self.grp_attrs,
            self.ds_attrs,
            expected,
        )

    def test_array_inserter_complex_scalar_array(self):
        data = np.array(np.pi + 2j)
        self.ds_attrs['ArraySize'] = (1, 1)
        expected = np.array([data.real, data.imag]).reshape(2, -1)
        self.assertSimpleInsert(
            ArrayInserter,
            data,
            self.grp_attrs,
            self.ds_attrs,
            expected,
        )

    def test_array_inserter_complex_empty(self):
        data = np.array([], complex)
        self.ds_attrs['ArraySize'] = (1, 0)
        self.grp_attrs['Empty'] = self.ds_attrs['Empty'] = 'yes'
        self.assertSimpleInsert(
            ArrayInserter,
            data,
            self.grp_attrs,
            self.ds_attrs,
            expected=None,
        )


class TestScalarInserter(InserterTestCase):

    def setUp(self):
        InserterTestCase.setUp(self)
        self.grp_attrs = dict(
            RecordType='numeric',
            Empty='no',
        )
        self.ds_attrs = dict(
            RecordType='numeric',
            Empty='no',
            Complex='no',
            Sparse='no',
        )

    def tearDown(self):
        del self.grp_attrs
        del self.ds_attrs
        InserterTestCase.tearDown(self)

    def test_scalar_inserter(self):
        data = 3
        expected = np.atleast_2d(data)
        self.assertSimpleInsert(
            ScalarInserter,
            data,
            self.grp_attrs,
            self.ds_attrs,
            expected
        )

    def test_scalar_inserter_empty(self):
        data = np.nan
        self.grp_attrs['Empty'] = self.ds_attrs['Empty'] = 'yes'
        self.assertSimpleInsert(
            ScalarInserter,
            data,
            self.grp_attrs,
            self.ds_attrs,
            expected=None
        )


class TestScalarInserterComplex(NumericInserterTestCase):

    def setUp(self):
        NumericInserterTestCase.setUp(self)
        self.ds_attrs['Complex'] = 'yes'
        self.ds_attrs['ArraySize'] = (1, 1)

    def test_scalar_inserter_complex(self):
        data = 1 + 1j
        expected = np.array([data.real, data.imag]).reshape(2, 1)
        self.assertSimpleInsert(
            ScalarInserter,
            data,
            self.grp_attrs,
            self.ds_attrs,
            expected,
        )

    def test_scalar_inserter_complex_empty(self):
        data = np.nan * (1 + 1j)
        self.grp_attrs['Empty'] = self.ds_attrs['Empty'] = 'yes'
        self.assertSimpleInsert(
            ScalarInserter,
            data,
            self.grp_attrs,
            self.ds_attrs,
            expected=None,
        )


class TestSparseInserter(NumericInserterTestCase):

    def setUp(self):
        NumericInserterTestCase.setUp(self)
        self.ds_attrs['Sparse'] = 'yes'

    def test_sparse_inserter(self):
        data = coo_matrix((np.arange(5), (np.arange(1, 6), np.arange(2, 7))))
        expected = np.array([data.row + 1, data.col + 1, data.data])
        self.assertSimpleInsert(
            SparseInserter,
            data,
            self.grp_attrs,
            self.ds_attrs,
            expected,
        )

    def test_sparse_inserter_complex(self):
        data = coo_matrix(
            (np.arange(5)+1j, (np.arange(1, 6), np.arange(2, 7)))
        )
        self.ds_attrs['Complex'] = 'yes'
        self.ds_attrs['ArraySize'] = (6, 7)
        expected = np.array([
            [10, 18, 26, 34, 42],
            np.arange(5),
            np.ones(5),
        ])
        self.assertSimpleInsert(
            SparseInserter,
            data,
            self.grp_attrs,
            self.ds_attrs,
            expected,
        )
