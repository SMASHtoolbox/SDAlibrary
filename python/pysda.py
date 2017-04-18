import abc
import os

import h5py
import numpy as np
import traits.has_traits
from traits.api import HasTraits


class M_SDAFile(abc.ABCMeta, traits.has_traits.MetaHasTraits):
    pass


class SDAFile(h5py.File, HasTraits):
    __metaclass__ = M_SDAFile
    # TODO: At the moment, if an exception is raised, after the super call
    # the file creation succeeds, but does not bind to a variable.
    def __init__(self, name, mode=None, driver=None,
                 libver=None, userblock_size=None, swmr=False, **kwds):
        exists = os.path.exists(name)
        h5py.File.__init__(self, name, mode=mode, driver=driver,
                           libver=libver, userblock_size=userblock_size, swmr=swmr,
                           **kwds)
        if mode in ['w', 'x', 'w-']:
            self.attrs['FileFormat'] = 'SDA'
            self._file_format = 'SDA'
            self.attrs['FormatVersion'] = '1.1'
            self._format_version = '1.1'
            self.attrs['Writable'] = 'yes'
            self._writable = 'yes'
            self._created = 'now'  # TODO
            self._updated = 'now'  # TODO

        elif mode in ['r', 'r+']:
            self._file_format = self.attrs['FileFormat']
            self._format_version = self.attrs['FormatVersion']
            self._writable = self.attrs['Writable']
            self._created = self.attrs['Created']
            self._updated = self.attrs['Updated']

        elif mode == 'a' or mode is None:
            if exists:
                self._file_format = self.attrs['FileFormat']
                self._format_version = self.attrs['FormatVersion']
                self._writable = self.attrs['Writable']
                self._created = self.attrs['Created']
                self._updated = self.attrs['Updated']
            else:
                self.attrs['FileFormat'] = 'SDA'
                self._file_format = 'SDA'
                self.attrs['FormatVersion'] = '1.1'
                self._format_version = '1.1'
                self.attrs['Writable'] = 'yes'
                self._writable = 'yes'
                self.attrs['Created'] = 'now'  # TODO
                self._created = 'now'  # TODO
                self.attrs['Updated'] = 'now'  # TODO
                self._updated = 'now'  # TODO
        else:
            # This is probably handled in the super call
            raise AttributeError('Mode {} is invalid.'.format(mode))


    def create_record(self, record_name, record_type):
        allowed_types = ['numeric', 'logical', 'character', 'function',
                         'cell', 'structure', 'structures', 'object',
                         'objects', 'file', 'split']
        if record_type.lower() not in allowed_types:
            raise AttributeError('Type {} is not a record type.'.format(record_type))
        record_group = self.create_group(record_name)

    def _create_numeric(self, record_name, dtype, shape=None, data=None, maxshape=None, **kwds):
        allowed_dtypes = ['int8', 'int16', 'int32', 'int64',
                          'uint8', 'uint16', 'uint32', 'uint64',
                          'float16', 'float32', 'float64']
        record_group = self.create_group(record_name)
        record_group.attrs['RecordType'] = 'Numeric'
        if data is None:
            record_group.attrs['Empty'] = 'yes'
        else:
            record_group.attrs['Empty'] = 'no'
        if np.dtype(dtype) not in allowed_dtypes:
            raise TypeError('{} is not an allowed type for numeric records.'.format(dtype))
        record_group.attrs['Deflate'] = str(kwds.get('Compression',0))
        data = record_group.create_dataset(record_name, dtype=dtype, shape=shape, data=data,
                                           **kwds)
        data.attrs['RecordType'] = record_group.attrs['RecordType']
        data.attrs['Empty'] = record_group.attrs['Empty']

    def _create_logical(self, record_name, dtype, shape=None, data=None, maxshape=None, **kwds):
        allowed_types = ['uint8']
        record_group = self.create_group(record_name)
        record_group.attrs['RecordType'] = 'Logical'
        if data is None:
            record_group.attrs['Empty'] = 'yes'
        else:
            record_group.attrs['Empty'] = 'no'
        record_group.attrs['Deflate'] = str(kwds.get('Compression',0))
        data = record_group.create_dataset(record_name, dtype=dtpye, shape=shape, data=data,
                                           **kwds)
        data.attrs['RecordType'] = record_group.attrs['RecordType']
        data.attrs['Emplty'] = record_group.attrs['Empty']

    def _create_character(self, record_name, shape=None, data=None, maxshape=None, **kwds):
            record_group = self.create_group(record_name)
            record_group.attrs['RecordType'] = 'Character'
            if data is None:
                record_group.attrs['Empty'] = 'yes'
            else:
                record_group.attrs['Empty'] = 'no'
            record_group.attrs['Deflate'] = str(kwds.get('Compression',0))
            data = record_group.create_dataset(record_name, dtype=dtpye, shape=shape, data=data,
                                               **kwds)
            data.attrs['RecordType'] = record_group.attrs['RecordType']
            data.attrs['Emplty'] = record_group.attrs['Empty']

    def _create_function(self, *args, **kwargs):
        raise NotImplemented(('Function records are matlab specific and cannot be created in',
                              'python.'))


        
