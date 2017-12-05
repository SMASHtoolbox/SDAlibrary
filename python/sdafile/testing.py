from contextlib import contextmanager
import os
import os.path as op
import tempfile
import unittest

import h5py
import numpy as np
from numpy.testing import assert_equal
from scipy.sparse import coo_matrix, eye

import sdafile
from sdafile.utils import get_decoded


DATA_DIR = op.join(op.abspath(op.dirname(sdafile.__file__)), 'tests', 'data')


def data_path(fname):
    """ Get path to data in test data directory. """
    return op.join(DATA_DIR, fname)


BAD_ATTRS = {
    'FileFormat': 'SDB',
    'FormatVersion': '0.5',
    'Writable': 'nope',
    'Created': '2017-01-01 01:23:45',
    'Updated': '2017-01-01 01:23:45',
}


GOOD_ATTRS = {
    'FileFormat': 'SDA',
    'FormatVersion': '1.1',
    'Writable': 'yes',
    'Created': '18-Aug-2017 01:23:45',
    'Updated': '18-Aug-2017 01:23:45',
}


FLOAT_VAL = 3.14159
INT_VAL = 3
BOOL_VAL = True
COMPLEX_VAL = 1.23 + 4.56j
STR_VAL = 'foo'
UNICODE_VAL = u'foo'

TEST_NUMERIC = [
    FLOAT_VAL,
    np.float32(FLOAT_VAL),
    np.float64(FLOAT_VAL),
    INT_VAL,
    np.long(INT_VAL),
    np.int8(INT_VAL),
    np.int16(INT_VAL),
    np.int32(INT_VAL),
    np.int64(INT_VAL),
    np.uint8(INT_VAL),
    np.uint16(INT_VAL),
    np.uint32(INT_VAL),
    np.uint64(INT_VAL),
    COMPLEX_VAL,
    np.complex64(COMPLEX_VAL),
    np.complex128(COMPLEX_VAL),
]

TEST_NUMERIC += [
    np.array(val) for val in TEST_NUMERIC
] + [
    np.array([val] * 4) for val in TEST_NUMERIC
] + [
    np.array([val] * 6).reshape(2, 3) for val in TEST_NUMERIC
]

TEST_LOGICAL = [
    BOOL_VAL,
    np.bool_(BOOL_VAL),
]

TEST_LOGICAL += [
    np.array(val) for val in TEST_LOGICAL
] + [
    np.array([val] * 4) for val in TEST_LOGICAL
] + [
    np.array([val] * 6).reshape(2, 3) for val in TEST_LOGICAL
]

TEST_CHARACTER = [
    STR_VAL,
    np.str_(STR_VAL),
    np.unicode_(STR_VAL),
]

TEST_CHARACTER += [
    np.array(list(val)).reshape(-1, 1) for val in TEST_CHARACTER
]


# Sparse matrix in all forms
TEST_SPARSE = [coo_matrix((np.arange(5), (np.arange(1, 6), np.arange(2, 7))))]
TEST_SPARSE.extend([
    TEST_SPARSE[0].tocsr(), TEST_SPARSE[0].tocsc(), TEST_SPARSE[0].tolil(),
    TEST_SPARSE[0].tobsr(), TEST_SPARSE[0].todok()
])

TEST_SPARSE_COMPLEX = [
    coo_matrix((np.arange(5) * (1 + 2j), (np.arange(1, 6), np.arange(2, 7))))
]
TEST_SPARSE_COMPLEX.extend([
    TEST_SPARSE_COMPLEX[0].tocsr(), TEST_SPARSE_COMPLEX[0].tocsc(),
    TEST_SPARSE_COMPLEX[0].tolil(), TEST_SPARSE_COMPLEX[0].tobsr(),
    TEST_SPARSE_COMPLEX[0].todok()
])

# lists, tuples
TEST_CELL = [
    ['hi', 'hello'],
    np.array(['hi', 'hello']),
    ['hello', np.arange(4)],
    ['hello', [True, np.arange(4)]],
    ['hello', (True, np.arange(4))],
    np.array(['hello', 3, [True, False, True], 3.14], dtype=object),
    np.array(
        [
            ['hello', 3],
            [[True, False, True], 3.14]
        ],
        dtype=object
    ),
    np.array(
        [
            ['hello', 3],
            [[True, False, True], 3.14]
        ],
        dtype=object,
        order='F',
    ),
    [
        {
            'foo': 'foo',
            'bar': np.arange(4),
            'baz': np.array([True, False])
        },
    ] * 3,
]

TEST_STRUCTURE = [
    {
        'foo': 'foo',
        'bar': np.arange(4),
        'baz': np.array([True, False])
    },
    {
        'foo': 'foo',
        'bar': [np.arange(4), np.array([True, False])]
    },
    {
        'strings': ['hi', 'hello'],
        'structure': {
            'foo': 'foo',
            'bar': np.arange(4),
            'baz': np.array([True, False])
        }
    },
]


# Unsupported
TEST_UNSUPPORTED = [
    eye(5, dtype=bool),  # sparse bool
    lambda x: x**2,
    {0},
    None,
]


# unsupported types, platform-specific
if hasattr(np, 'complex256'):
    TEST_UNSUPPORTED.append(np.complex256(0))
    TEST_UNSUPPORTED.append(np.arange(5, dtype=np.complex256))
    TEST_UNSUPPORTED.append(eye(5, dtype=np.complex256))
if hasattr(np, 'float128'):
    TEST_UNSUPPORTED.append(np.float128(0))
    TEST_UNSUPPORTED.append(np.arange(5, dtype=np.float128))
    TEST_UNSUPPORTED.append(eye(5, dtype=np.float128))
if hasattr(np, 'float16'):
    TEST_UNSUPPORTED.append(np.float16(0))
    TEST_UNSUPPORTED.append(np.arange(5, dtype=np.float16))
    TEST_UNSUPPORTED.append(eye(5, dtype=np.float16))


@contextmanager
def temporary_file(suffix='.sda'):
    pid, file_path = tempfile.mkstemp(suffix=suffix)
    os.close(pid)
    try:
        yield file_path
    finally:
        if op.isfile(file_path):
            os.remove(file_path)


@contextmanager
def temporary_h5file(suffix='.sda'):
    with temporary_file(suffix) as file_path:
        h5file = h5py.File(file_path, 'w')
        try:
            yield h5file
        finally:
            if h5file.id.valid:  # file is open
                h5file.close()


class MockRecordInserter(object):
    """ RecordInserter for testing.

    This must be used instantiated.

    """

    record_type = 'testing'

    def __init__(self, called):
        self.called = called

    def __call__(self, label, data, deflate, registry=None):
        # Mock initialization.
        self.label = label
        self.deflate = int(deflate)
        self.data = self.original_data = data
        self.empty = 'no'
        self._registry = registry
        return self

    def can_insert(self, data):
        return True

    def insert(self, h5file, description):
        self.called.append(description)


class InserterTestCase(unittest.TestCase):

    def setUp(self):
        from sdafile.record_inserter import InserterRegistry
        self.registry = InserterRegistry()

    def tearDown(self):
        del self.registry

    @contextmanager
    def insert(self, cls, label, data, deflate, description):
        inserter = cls(label, data, deflate, self.registry)
        with temporary_h5file() as h5file:
            inserter.insert(h5file, description)
            yield h5file

    def assertAttrs(self, dict_like, **attrs):
        assert_equal(attrs, get_decoded(dict_like))

    def assertRegistry(self, cls, data):
        """ Assert registry works for data. """
        self.assertTrue(cls.can_insert(data))
        found_cls = self.registry.get_inserter(data)
        self.assertIs(found_cls, cls)

    def assertSimpleInsert(self, cls, data, group_attrs, ds_attrs, expected):
        """ Test simple insertion. Pass expected=None to skip data check. """
        # Check registration
        self.assertRegistry(cls, data)

        # Test insertion
        label = 'test'
        with self.insert(cls, label, data, 0, 'desc') as h5file:
            grp = h5file[label]
            self.assertAttrs(
                grp.attrs,
                Description='desc',
                Deflate=0,
                **group_attrs
            )
            ds = grp[label]
            self.assertAttrs(ds.attrs, **ds_attrs)
            if expected is not None:
                stored = ds[()]
                assert_equal(stored, expected)
