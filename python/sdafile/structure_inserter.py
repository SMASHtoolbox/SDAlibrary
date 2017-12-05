from .record_inserter import CompositeRecordInserter, inserter
from .utils import is_valid_matlab_field_label, set_encoded


@inserter
class DictInserter(CompositeRecordInserter):
    """ Inserter for dicts. """

    record_type = 'structure'

    @staticmethod
    def can_insert(data):
        """ This can insert any dict, regardless of the contents. """
        return isinstance(data, dict)

    def record_group_attributes(self, dict_like):
        """ Record FieldNames along with other group attributes. """
        set_encoded(
            dict_like,
            RecordType=self.record_type,
            Empty=self.empty,
            Deflate=self.deflate,
            FieldNames=self.field_names
        )

    def prepare_data(self):
        """ Records FieldNames and Empty metadata, validates keys. """
        self.empty = 'yes' if len(self.data) == 0 else 'no'
        self._keys = sorted(key for key in self.data.keys())

        # Validate the keys
        for key in self._keys:
            if not is_valid_matlab_field_label(key):
                msg = "'{}' is not a valid MATLAB field label".format(key)
                raise ValueError(msg)
        self.field_names = " ".join(self._keys)

    def __iter__(self):
        for key in self._keys:
            sub_data = self.data[key]
            cls = self.registry.get_inserter(sub_data)
            if cls is None:
                msg = "Data not supported for insertion: {!r}".format(sub_data)
                raise ValueError(msg)
            inserter = cls(
                key, sub_data, self.deflate, registry=self.registry
            )
            yield inserter
