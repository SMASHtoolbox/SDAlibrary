import numpy as np

from .record_inserter import inserter
from .numeric_inserter import ArrayInserter as NumericArrayInserter
from .utils import set_encoded


@inserter
class FileInserter(NumericArrayInserter):
    """ Inserter for file-like objects.

    File groups register as 'file' type, whereas the data registers as
    'numeric'.

    """

    record_type = 'file'

    def record_dataset_attributes(self, dict_like):
        attrs = dict(
            RecordType='numeric',
            Empty=self.empty,
            Complex='no',
            Sparse='no',
        )
        set_encoded(dict_like, **attrs)

    @staticmethod
    def can_insert(data):
        """ Can insert file-like objects. """
        return hasattr(data, 'read')

    def prepare_data(self):
        contents = self.data.read()
        if not isinstance(contents, bytes):
            contents = contents.encode('ascii')
        self.data = np.frombuffer(contents, dtype=np.uint8)
        NumericArrayInserter.prepare_data(self)
