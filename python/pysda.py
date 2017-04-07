"""
:mod:`pysda` -- Python implementation of the SDA Library
===========================================================

Python implementation of the SDA Library

.. module::
   :synopsis: Python implementation of the SDA Library
"""
import abc
import time

import h5py

import traits
from traits.api import HasTraits


FORMAT_NAME = 'SDA'
FORMAT_VERSION = '1.1'


class MetaSDAFile(abc.ABCMeta, traits.has_traits.MetaHasTraits):
    pass


class SDAFile(h5py.File, HasTraits):  # pylint: disable=too-many-ancestors
    """The main entry point for interacting with the SDA format.
    This file object contains most variables and methods needed
    for using the file. Note that the data is provided in a 'raw'
    format, so the user is responsible for interprating the data
    in a manner useful to them. Specifically note that some of the
    pre-defined data-type the SDA library uses are matlab functions
    and may not be compatible with python. This issue may be
    addressed at a later time.
    """
    __metaclass__ = MetaSDAFile

    def __init__(self, file_name, mode='r'):
        super(SDAFile, self).__init__(file_name, mode=mode)
        if mode in ['w', 'w-', 'x']:
            self._format = FORMAT_NAME
            self.attrs['FileFormat'] = self._format
            self._format_version = FORMAT_VERSION
            self.attrs['FormatVersion'] = self._format_version
            self._writable = 'yes'
            self.attrs['Writable'] = self._writable
            self._created = time.localtime(None)
            self.attrs['Created'] = _format_time(self._created)
            self._updated = time.localtime(None)
            self.attrs['Updated'] = _format_time(self._updated)


def _format_time(time_struct):
    formatted_time = time.strftime("%d-%b-%Y %H:%M:%S", time_struct)
    return formatted_time


class MetaRecord(abc.ABCMeta, traits.has_traits.MetaHasTraits):  # Oh dear...
    """Defined class for making multiple inhertance work
    on h5py.File and HasTraits, since they are both metaclasses.
    """
    pass


class Record(h5py.Group, HasTraits):
    """The base class for SDA records. Contains logic for enforcing
    constraints on its members."""
    __metaclass__ = MetaRecord

    def __init__(self, record_type):
        self.record_type = record_type
