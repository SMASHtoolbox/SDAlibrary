import os

import h5py
from h5py import h5g
from h5py._hl.base import phil, with_phil

from pysda.groups import SDAGroup

FILE_FORMAT = 'SDA'
FORMAT_VERSION = '1.1'
DEFAULT_WRITABLE = 'yes'


class SDAFile(h5py.File):
    """
    Represents an SDAFile. Needs to have all the appropriate attributes.
    """
    def __init__(self, name, mode=None, driver=None, libver=None,
                 userblock_size=None, swmr=False, **kwds):
        super(SDAFile, self).__init__(name, mode=mode, driver=driver,
                                      libver=libver,
                                      userblock_size=userblock_size, swmr=swmr,
                                      **kwds)
        self._set_initial_sda_attributes()
        self._file_format = self.attrs['FileFormat']
        self._format_version = self.attrs['FormatVersion']
        self._writable = self.attrs['Writable']
        self._created = self.attrs['Created']
        self._updated = self.attrs['Updated']

    def __getitem__(self, key):
        # Can raise a type error
        value = super(SDAFile, self).__getitem__(key)
        return SDAGroup(value)

    def get(self, name, default=None, getclass=None, getlink=None):
        value = super(SDAFile, self).get(name, default=default,
                                         getclass=getclass, getlink=getlink)
        return value

    @property
    def file_format(self):
        return self._file_format

    @file_format.setter
    def file_format(self, value):
        raise Exception("This attribute should not be changed.")

    @property
    def format_version(self):
        return self._format_version

    @format_version.setter
    def format_version(self, value):
        raise Exception("This attribute should not be changed.")

    @property
    def writable(self):
        return self._writable

    @writable.setter
    def writable(self, value):
        raise Exception("This attribute should not be changed.")

    @property
    def created(self):
        return self._created

    @created.setter
    def created(self, value):
        raise Exception("This attribute should not be changed.")

    @property
    def updated(self):
        return self._updated

    @updated.setter
    def updated(self, value):
        self._updated = 'TODO'  # TODO: Get current time and format it
        self.attrs['Updated'] = self._updated

    def __repr__(self):
        if not self.id:
            r = u'<Closed SDA file>'
        else:
            filename = self.filename
            if isinstance(filename, bytes):
                filename = filename.decode('utf8', 'replace')
            r = u'<SDAFile "{}" (mode {})>'.format(os.path.basename(filename),
                                                   self.mode)
        return r

    def _set_initial_sda_attributes(self):
        if 'FileFormat' not in self.attrs:
            self.attrs['FileFormat'] = FILE_FORMAT
        if 'FormatVersion' not in self.attrs:
            self.attrs['FormatVersion'] = FORMAT_VERSION
        if 'Writable' not in self.attrs:
            self.attrs['Writable'] = DEFAULT_WRITABLE
        if 'Created' not in self.attrs:
            self.attrs['Created'] = 'TODO'  # TODO: get the current time
        if 'Updated' not in self.attrs:
            self.attrs['Updated'] = 'TODO'  # TODO: get the current time

    def create_group(self, name):  # Overrides h5py.Group.create_group
        raw = super(SDAFile, self).create_group(name)
        return SDAGroup(raw)
