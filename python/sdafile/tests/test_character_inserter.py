import numpy as np

from sdafile.character_inserter import (
    ArrayInserter, BytesInserter, StringInserter,
)
from sdafile.testing import InserterTestCase


class TestCharacterInserter(InserterTestCase):

    def setUp(self):
        InserterTestCase.setUp(self)
        self.grp_attrs = dict(
            RecordType='character',
            Empty='no',
        )
        self.ds_attrs = dict(
            RecordType='character',
            Empty='no',
        )

    def tearDown(self):
        del self.grp_attrs
        del self.ds_attrs
        InserterTestCase.tearDown(self)

    def test_array_inserter(self):
        data = np.frombuffer(b'01', 'S1')
        expected = np.array([48, 49], np.uint8).reshape(2, -1)
        self.assertSimpleInsert(
            ArrayInserter,
            data,
            self.grp_attrs,
            self.ds_attrs,
            expected
        )

    def test_array_inserter_reshaped(self):
        data = np.frombuffer(b'01', 'S1').reshape(2, -1)
        expected = np.array([48, 49], np.uint8).reshape(-1, 2)
        self.assertSimpleInsert(
            ArrayInserter,
            data,
            self.grp_attrs,
            self.ds_attrs,
            expected
        )

    def test_array_inserter_empty(self):
        data = np.array([], 'S1')
        self.grp_attrs['Empty'] = self.ds_attrs['Empty'] = 'yes'
        self.assertSimpleInsert(
            ArrayInserter,
            data,
            self.grp_attrs,
            self.ds_attrs,
            expected=None
        )

    def test_string_inserter(self):
        data = '01'
        expected = np.array([48, 49], np.uint8).reshape(2, -1)
        self.assertSimpleInsert(
            StringInserter,
            data,
            self.grp_attrs,
            self.ds_attrs,
            expected,
        )

    def test_string_inserter_unicode(self):
        data = u'01'
        expected = np.array([48, 49], np.uint8).reshape(2, -1)
        self.assertSimpleInsert(
            StringInserter,
            data,
            self.grp_attrs,
            self.ds_attrs,
            expected,
        )

    def test_string_inserter_empty(self):
        data = ''
        self.grp_attrs['Empty'] = self.ds_attrs['Empty'] = 'yes'
        self.assertSimpleInsert(
            StringInserter,
            data,
            self.grp_attrs,
            self.ds_attrs,
            expected=None
        )

    def test_bytes_inserter(self):
        data = b'01'
        expected = np.array([48, 49], np.uint8).reshape(2, -1)
        self.assertSimpleInsert(
            BytesInserter,
            data,
            self.grp_attrs,
            self.ds_attrs,
            expected,
        )

    def test_bytes_inserter_empty(self):
        data = b''
        self.grp_attrs['Empty'] = self.ds_attrs['Empty'] = 'yes'
        self.assertSimpleInsert(
            BytesInserter,
            data,
            self.grp_attrs,
            self.ds_attrs,
            expected=None
        )
