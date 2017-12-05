import numpy as np

from .record_inserter import CompositeRecordInserter, inserter
from .utils import cell_label, set_encoded


class CellRecordInserter(CompositeRecordInserter):
    """ Base class for cell record inserters. """

    record_type = 'cell'

    def record_group_attributes(self, dict_like):
        set_encoded(
            dict_like,
            RecordType=self.record_type,
            Empty=self.empty,
            Deflate=self.deflate,
            RecordSize=self.record_size,
        )


@inserter
class ListInserter(CellRecordInserter):
    """ Inserter for lists and tuples. """

    @staticmethod
    def can_insert(data):
        """ This can insert any list or tuple regardless of the contents. """
        return isinstance(data, (list, tuple))

    def prepare_data(self):
        """ Records RecordSize metadata. """
        self.empty = 'yes' if len(self.data) == 0 else 'no'
        self.record_size = (1, len(self.data))

    def __iter__(self):
        for i, sub_data in enumerate(self.data, start=1):
            cls = self.registry.get_inserter(sub_data)
            if cls is None:
                msg = "Data not supported for insertion: {!r}".format(sub_data)
                raise ValueError(msg)
            label = cell_label(i)
            inserter = cls(
                label, sub_data, self.deflate, registry=self.registry,
            )
            yield inserter


@inserter
class ArrayInserter(ListInserter):
    """ Inserter for arrays of objects. """

    @staticmethod
    def can_insert(data):
        """ This can insert arrays of objects or string-like things. """
        if not isinstance(data, np.ndarray):
            return False
        dtypes = (np.object_, np.unicode_, np.str_)
        return issubclass(data.dtype.type, dtypes)

    def prepare_data(self):
        """ Records RecordSize and Empty metadata. """
        self.record_size = np.atleast_2d(self.data).shape
        self.data = self.original_data.ravel(order='F')
        self.empty = 'yes' if self.data.size == 0 else 'no'
