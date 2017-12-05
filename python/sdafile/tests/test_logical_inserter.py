import numpy as np

from sdafile.logical_inserter import ArrayInserter, ScalarInserter
from sdafile.testing import InserterTestCase


class TestLogicalInserter(InserterTestCase):

    def setUp(self):
        InserterTestCase.setUp(self)
        self.grp_attrs = dict(
            RecordType='logical',
            Empty='no',
        )
        self.ds_attrs = dict(
            RecordType='logical',
            Empty='no',
        )

    def tearDown(self):
        del self.grp_attrs
        del self.ds_attrs
        InserterTestCase.tearDown(self)

    def test_array_inserter_basic(self):
        data = np.array([True, False])
        expected = np.array([1, 0], np.uint8).reshape(2, -1)
        self.assertSimpleInsert(
            ArrayInserter,
            data,
            self.grp_attrs,
            self.ds_attrs,
            expected
        )

    def test_array_inserter_array_scalar(self):
        data = np.array(True)
        expected = np.array([[1]], np.uint8)
        self.assertSimpleInsert(
            ArrayInserter,
            data,
            self.grp_attrs,
            self.ds_attrs,
            expected
        )

    def test_array_inserter_empty(self):
        data = np.array([], bool)
        self.grp_attrs['Empty'] = self.ds_attrs['Empty'] = 'yes'
        self.assertSimpleInsert(
            ArrayInserter,
            data,
            self.grp_attrs,
            self.ds_attrs,
            expected=None,
        )

    def test_scalar_inserter_bool(self):
        data = True
        expected = np.array([[1]], np.uint8)
        self.assertSimpleInsert(
            ScalarInserter,
            data,
            self.grp_attrs,
            self.ds_attrs,
            expected,
        )

    def test_scalar_inserter_bool_(self):
        data = np.bool_(True)
        expected = np.array([[1]], np.uint8)
        self.assertSimpleInsert(
            ScalarInserter,
            data,
            self.grp_attrs,
            self.ds_attrs,
            expected,
        )
