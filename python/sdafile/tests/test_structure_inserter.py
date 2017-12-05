import numpy as np
from numpy.testing import assert_equal

from sdafile.structure_inserter import DictInserter
from sdafile.testing import InserterTestCase


class TestStructInserter(InserterTestCase):

    def test_dict_inserter_basic(self):
        data = {'a': 3.14, 'b': '01', 'c': {'d': True, 'e': np.array([])}}
        grp_attrs = dict(
            RecordType='structure',
            Empty='no',
            FieldNames='a b c',
            Description='desc',
            Deflate=0,
        )
        self.assertRegistry(DictInserter, data)
        label = 'test'
        description = 'desc'
        with self.insert(DictInserter, label, data, 0, description) as h5file:
            grp = h5file[label]
            self.assertAttrs(
                grp.attrs,
                **grp_attrs
            )

            ds_a = grp['a']
            self.assertAttrs(
                ds_a.attrs,
                RecordType='numeric',
                Empty='no',
                Complex='no',
                Sparse='no',
            )
            data = ds_a[()]
            expected = np.atleast_2d(3.14)
            assert_equal(data, expected)

            ds_b = grp['b']
            self.assertAttrs(
                ds_b.attrs,
                RecordType='character',
                Empty='no',
            )
            data = ds_b[()]
            expected = np.array([48, 49], np.uint8).reshape(2, 1)
            assert_equal(data, expected)

            grp_c = grp['c']
            self.assertAttrs(
                grp_c.attrs,
                RecordType='structure',
                Deflate=0,
                FieldNames='d e',
                Empty='no',
            )

            ds_d = grp_c['d']
            self.assertAttrs(
                ds_d.attrs,
                RecordType='logical',
                Empty='no',
            )
            data = ds_d[()]
            expected = np.array([[1]], np.uint8)
            assert_equal(data, expected)

            ds_e = grp_c['e']
            self.assertAttrs(
                ds_e.attrs,
                RecordType='numeric',
                Empty='yes',
                Complex='no',
                Sparse='no',
            )

    def test_dict_inserter_empty(self):
        data = {}
        grp_attrs = dict(
            RecordType='structure',
            Empty='yes',
            FieldNames='',
            Description='desc',
            Deflate=0,
        )
        self.assertRegistry(DictInserter, data)
        label = 'test'
        description = 'desc'
        with self.insert(DictInserter, label, data, 0, description) as h5file:
            grp = h5file[label]
            self.assertAttrs(
                grp.attrs,
                **grp_attrs
            )
