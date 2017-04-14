import h5py
import numpy as np


class Record(h5py.Group):
    def __init__(self, binding_group):
        super(Record, self).__init__(binding_group.id)
        self.local_name = self.name.split('/')[-1]

    # def create_dataset(*args, **kwargs):
    #     data_name = self.get_local_name()
    #     self.file.update()

    def __getitem__(self, key):
        val = super(Record, self).__getitem__(key)
        casted_value = cast(val)
        return casted_value


class PrimitiveRecord(Record):
    def __init__(self, binding_group):
        super(PrimitiveRecord, self).__init__(binding_group)
        # self.verify_record_format()

    # def _verify_only_one_dataset(self):
    #     if len(self.values()) > 1: # this is a problem since it calls record's __getitem__
    #     # and record's __getitem__ cast's variables
    #         raise AttributeError
    #
    # def _verify_dataset_name(self):
    #     if self.keys()[0] != self.local_name:
    #         raise AttributeError
    #
    # def verify_record_format(self):
    #     self._verify_only_one_dataset()
    #     self._verify_dataset_name()

    def create_dataset(self, shape=None, dtype=None, data=None, **kwargs):
        super(PrimitiveRecord, self).create_dataset(shape=shape,
                                                    dtype=dtype, data=data,
                                                    **kwargs)


class NumericRecord(PrimitiveRecord):
    def __init__(self, binding_group):
        super(NumericRecord, self).__init__(binding_group)

    def create_dataset(self, shape=None, dtype=None, data=None, **kwargs):
        self.verify_dtype(dtype)
        super(NumericRecord, self).create_dataset(shape=shape, dtype=dtype,
                                                  data=data, **kwargs)

    def verify_dtype(dtype):
        allowed_dtypes = ['uint8', 'uint16', 'uint32', 'uint64', 'int8',
                          'int16', 'int32', 'int64', 'float16', 'float32',
                          'float64']
        dtype = np.dtype(dtype)
        if dtype not in allowed_dtypes:
            raise AttributeError('Cannot set NumericRecord with dtype {}'
                                 .format(dtype))


def cast(group):
    # if isinstance(group, h5py.Dataset):
    #     return group
    if 'RecordType' not in group.attrs.keys() and group.name != '/':
        raise AttributeError('Invalid SDA format.')
    if group.name == '/':
        return group
    if group.attrs['RecordType'].lower() == 'numeric':
        print 'casted'
        return NumericRecord(group)
