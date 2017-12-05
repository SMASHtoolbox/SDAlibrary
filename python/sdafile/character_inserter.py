import numpy as np

from .record_inserter import SimpleRecordInserter, inserter


@inserter
class ArrayInserter(SimpleRecordInserter):
    """ Inserter for character arrays. """

    record_type = 'character'

    @staticmethod
    def can_insert(data):
        """ Insert boolean arrays. """
        if not isinstance(data, np.ndarray):
            return False
        return data.dtype == np.dtype('S1')

    def prepare_data(self):
        data = self.data.view(np.uint8)
        # Matlab stores the transpose of 2D arrays. This must be applied here.
        self.data = np.atleast_2d(data).T
        self.empty = 'yes' if self.data.size == 0 else 'no'


@inserter
class StringInserter(ArrayInserter):
    """ Inserter for strings. """

    @staticmethod
    def can_insert(data):
        """ Insert bool and np.bool_ """
        return isinstance(data, (str, np.unicode))

    def prepare_data(self):
        self.data = np.frombuffer(self.data.encode('ascii'), 'S1')
        ArrayInserter.prepare_data(self)


if bytes is str:  # python 3

    BytesInserter = StringInserter

else:  # python 2

    @inserter
    class BytesInserter(ArrayInserter):
        """ Inserter for bytes. """

        @staticmethod
        def can_insert(data):
            """ Insert bytes. """
            return isinstance(data, bytes)

        def prepare_data(self):
            self.data = np.frombuffer(self.data, 'S1')
            ArrayInserter.prepare_data(self)
