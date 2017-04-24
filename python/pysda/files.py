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
        try:
            self._file_format = self.attrs['FileFormat']
            self._format_version = self.attrs['FormatVersion']
            self._writable = self.attrs['Writable']
            self._created = self.attrs['Created']
            self._updated = self.attrs['Updated']
        except KeyError:
            if self.mode == 'r':
                raise
            self._file_format = 'SDA'
            self.attrs['FileFormat'] = self._file_format
            self._format_version = '1.1'
            self.attrs['FormatVersion'] = self._format_version
            self._writable = 'yes'
            self.attrs['Writable'] = self._writable
            self._created = time.strftime('%d-%b-%Y %H:%M:%S')
            self.attrs['Created'] = self._created
            self._updated = time.strftime('%d-%b-%Y %H:%M:%S')
            self.attrs['Updated'] = self._updated
