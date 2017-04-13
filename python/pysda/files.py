import os
import time

import h5py

import pysda.groups


class SDAFile(h5py.File):
    def __init__(self, name, mode=None, driver=None, libver=None,
                 userblock_size=None, swmr=None, **kwargs):
        super(SDAFile, self).__init__(name, mode=mode, driver=driver,
                                      libver=libver,
                                      userblock_size=userblock_size,
                                      swmr=swmr, **kwargs)
        if mode in ['r', 'r+'] or mode is None:
            self._file_format = self.attrs['FileFormat']
            self._format_version = self.attrs['FormatVersion']
            self._writable = self.attrs['Writable']
            self._created = self.attrs['Created']
            self._updated = self.attrs['Updated']
        else:
            self._file_format = 'SDA'
            self._format_version = '1.1'
            self._writable = 'yes'
            self._created = time.strftime('%d-%b-%Y %H:%M:%S')
            self._updated = time.strftime('%d-%b-%Y %H:%M:%S')

    def __getitem__(self, key):
        val = super(SDAFile, self).__getitem__(key)
        val = pysda.groups.cast(val)
        return val

    @property
    def file_format(self):
        return self._file_format

    @property
    def format_version(self):
        return self._format_version

    @property
    def writable(self):
        return self._writable

    @writable.setter
    def writable(self, other):
        if other.lower() not in ['yes', 'no']:
            raise AttributeError
        self._writable = other

    @property
    def created(self):
        return self._created

    @property
    def updated(self):
        return self._updated

    def update(self):
        self._updated = time.strftime('%d-%b-%Y %H:%M:%S')

    def create_dataset(self, *args, **kwargs):
        raise TypeError('There can be no datasets in the root group.')
