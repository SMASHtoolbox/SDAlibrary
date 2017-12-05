import numpy as np
from numpy.testing import assert_equal

from sdafile.cell_inserter import ArrayInserter, ListInserter
from sdafile.testing import InserterTestCase


class TestCellInserter(InserterTestCase):

    def test_list_inserter_basic(self):
        data = [3.14, '01', [True, np.array([])]]
        grp_attrs = dict(
            RecordType='cell',
            Empty='no',
            RecordSize=(1, 3),
            Description='desc',
            Deflate=0,
        )
        self.assertRegistry(ListInserter, data)
        label = 'test'
        description = 'desc'
        with self.insert(ListInserter, label, data, 0, description) as h5file:
            grp = h5file[label]
            self.assertAttrs(
                grp.attrs,
                **grp_attrs
            )

            ds_1 = grp['element 1']
            self.assertAttrs(
                ds_1.attrs,
                RecordType='numeric',
                Empty='no',
                Complex='no',
                Sparse='no',
            )
            data = ds_1[()]
            expected = np.atleast_2d(3.14)
            assert_equal(data, expected)

            ds_2 = grp['element 2']
            self.assertAttrs(
                ds_2.attrs,
                RecordType='character',
                Empty='no',
            )
            data = ds_2[()]
            expected = np.array([48, 49], np.uint8).reshape(2, 1)
            assert_equal(data, expected)

            grp_3 = grp['element 3']
            self.assertAttrs(
                grp_3.attrs,
                RecordType='cell',
                Deflate=0,
                RecordSize=(1, 2),
                Empty='no',
            )

            ds_3_1 = grp_3['element 1']
            self.assertAttrs(
                ds_3_1.attrs,
                RecordType='logical',
                Empty='no',
            )
            data = ds_3_1[()]
            expected = np.array([[1]], np.uint8)
            assert_equal(data, expected)

            ds_3_2 = grp_3['element 2']
            self.assertAttrs(
                ds_3_2.attrs,
                RecordType='numeric',
                Empty='yes',
                Complex='no',
                Sparse='no',
            )

    def test_array_inserter_basic(self):
        data = np.array(
            [3.14, '01', [True, np.array([])]], dtype=object
        ).reshape(3, 1)
        grp_attrs = dict(
            RecordType='cell',
            Empty='no',
            RecordSize=(3, 1),
            Description='desc',
            Deflate=0,
        )
        self.assertRegistry(ArrayInserter, data)
        label = 'test'
        description = 'desc'
        with self.insert(ArrayInserter, label, data, 0, description) as h5file:
            grp = h5file[label]
            self.assertAttrs(
                grp.attrs,
                **grp_attrs
            )

            ds_1 = grp['element 1']
            self.assertAttrs(
                ds_1.attrs,
                RecordType='numeric',
                Empty='no',
                Complex='no',
                Sparse='no',
            )
            data = ds_1[()]
            expected = np.atleast_2d(3.14)
            assert_equal(data, expected)

            ds_2 = grp['element 2']
            self.assertAttrs(
                ds_2.attrs,
                RecordType='character',
                Empty='no',
            )
            data = ds_2[()]
            expected = np.array([48, 49], np.uint8).reshape(2, 1)
            assert_equal(data, expected)

            grp_3 = grp['element 3']
            self.assertAttrs(
                grp_3.attrs,
                RecordType='cell',
                Deflate=0,
                RecordSize=(1, 2),
                Empty='no',
            )

            ds_3_1 = grp_3['element 1']
            self.assertAttrs(
                ds_3_1.attrs,
                RecordType='logical',
                Empty='no',
            )
            data = ds_3_1[()]
            expected = np.array([[1]], np.uint8)
            assert_equal(data, expected)

            ds_3_2 = grp_3['element 2']
            self.assertAttrs(
                ds_3_2.attrs,
                RecordType='numeric',
                Empty='yes',
                Complex='no',
                Sparse='no',
            )

    def test_list_inserter_empty(self):
        data = []
        grp_attrs = dict(
            RecordType='cell',
            Empty='yes',
            RecordSize=(1, 0),
            Description='desc',
            Deflate=0,
        )
        self.assertRegistry(ListInserter, data)
        label = 'test'
        description = 'desc'
        with self.insert(ListInserter, label, data, 0, description) as h5file:
            grp = h5file[label]
            self.assertAttrs(
                grp.attrs,
                **grp_attrs
            )

    def test_array_inserter_empty(self):
        data = np.array([], object)
        grp_attrs = dict(
            RecordType='cell',
            Empty='yes',
            RecordSize=(1, 0),
            Description='desc',
            Deflate=0,
        )
        self.assertRegistry(ArrayInserter, data)
        label = 'test'
        description = 'desc'
        with self.insert(ArrayInserter, label, data, 0, description) as h5file:
            grp = h5file[label]
            self.assertAttrs(
                grp.attrs,
                **grp_attrs
            )
