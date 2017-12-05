import numpy as np

from .record_inserter import SimpleRecordInserter, inserter


@inserter
class ArrayInserter(SimpleRecordInserter):
    """ Inserter for boolean arrays. """

    record_type = 'logical'

    @staticmethod
    def can_insert(data):
        """ Can insert boolean arrays. """
        if not isinstance(data, np.ndarray):
            return False
        return np.issubdtype(data.dtype, np.bool_)

    def prepare_data(self):
        data = self.data.astype(np.uint8).clip(0, 1)
        # Matlab stores the transpose of 2D arrays. This must be applied here.
        self.data = np.atleast_2d(data).T
        self.empty = 'yes' if self.data.size == 0 else 'no'


@inserter
class ScalarInserter(ArrayInserter):
    """ Inserter for bool and np.bool_. """

    @staticmethod
    def can_insert(data):
        """ Can insert bool and np.bool_ """
        return isinstance(data, (bool, np.bool_))

    def prepare_data(self):
        """ Records RecordSize metadata. """
        self.data = np.asarray(self.data)
        ArrayInserter.prepare_data(self)
