import numpy as np
from scipy.sparse import issparse

from .record_inserter import SimpleRecordInserter, inserter
from .utils import UNSUPPORTED_NUMERIC_TYPE_CODES, set_encoded


class BaseNumericInserter(SimpleRecordInserter):
    """ Base inserter for numeric types. """

    record_type = 'numeric'

    def record_dataset_attributes(self, dict_like):
        attrs = dict(
            RecordType=self.record_type,
            Empty=self.empty,
            Complex=self.complex,
            Sparse=self.sparse,
        )
        if self.complex == 'yes':
            attrs['ArraySize'] = self.array_size
        set_encoded(dict_like, **attrs)


@inserter
class ArrayInserter(BaseNumericInserter):
    """ Inserter for numeric arrays. """

    @staticmethod
    def can_insert(data):
        """ Can insert numeric arrays. """
        if not isinstance(data, np.ndarray):
            return False
        if data.dtype.char in UNSUPPORTED_NUMERIC_TYPE_CODES:
            return False
        return np.issubdtype(data.dtype, np.number)

    def prepare_data(self):
        self.empty = 'no'
        if np.iscomplexobj(self.data):
            # This prepares the data as a 2xN array containing the real and
            # imaginary values of the input as rows 0 and 1.
            self.complex = 'yes'
            data = np.atleast_2d(self.data)
            self.array_size = data.shape
            data = data.ravel(order='F')
            self.data = np.array([data.real, data.imag]).reshape(2, -1)
            if self.array_size == (1, 1) and np.all(np.isnan(self.data)):
                self.empty = 'yes'
        else:
            self.complex = 'no'
            self.data = np.atleast_2d(self.data).T
            self.array_size = None
            if self.data.shape == (1, 1) and np.all(np.isnan(self.data)):
                self.empty = 'yes'

        self.sparse = 'no'
        self.empty = 'yes' if self.data.size == 0 else self.empty


@inserter
class ScalarInserter(ArrayInserter):
    """ Inserter for numeric scalars. """

    @staticmethod
    def can_insert(data):
        """ Can insert numeric scalars. """
        types = (float, complex, int, np.long)
        if isinstance(data, types) and not isinstance(data, bool):
            return True
        elif isinstance(data, np.number):
            return data.dtype.char not in UNSUPPORTED_NUMERIC_TYPE_CODES

    def prepare_data(self):
        """ Records RecordSize metadata. """
        self.data = np.asarray(self.data)
        ArrayInserter.prepare_data(self)


@inserter
class SparseInserter(BaseNumericInserter):
    """ Inserter for sparse, numeric arrays. """

    @staticmethod
    def can_insert(data):
        """ Can insert numeric scalars. """
        if not issparse(data):
            return False
        if data.dtype.char in UNSUPPORTED_NUMERIC_TYPE_CODES:
            return False
        return np.issubdtype(data.dtype, np.number)

    def prepare_data(self):
        """ Records RecordSize metadata. """
        self.sparse = 'yes'
        data = self.data.tocoo()
        if np.issubdtype(self.data.dtype, np.complexfloating):
            self.complex = 'yes'
            self.array_size = data.shape
            indices = np.ravel_multi_index((data.row, data.col), data.shape)
            self.data = np.vstack([
                indices + 1, data.data.real, data.data.imag
            ])
        else:
            self.complex = 'no'
            self.array_size = None
            # 3 x N, [row, column, value], 1-based
            self.data = np.array([data.row + 1, data.col + 1, data.data])
