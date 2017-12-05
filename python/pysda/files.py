import abc
import os
import time

import h5py

from traits.api import HasTraits

import pysda.groups

class MetaSDAFile(abc.ABCMeta, traits.has_traits.MetaHasTraits):
    pass

class SDAFile(h5py.File, HasTraits):
    __metaclass__ = MetaSDAFile

    def __init__(self, name, mode=None, driver=None, libver=None,
                 userblock_size=None, swmr=None, **kwargs):
        exists = os.path.exists(name)
        h5py.File.__init__(self, name, mode=mode, driver=driver,
                           libver=libver, userblock_size=userblock_size,
                           swmr=swmr, **kwargs)
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


