"""
:mod:`pysda` -- Python implementation of the SDA Library
===========================================================

Python implementation of the SDA Library

.. module::
   :synopsis: Python implementation of the SDA Library
"""
import time


import h5py

from traits.api import HasTraits


FORMAT_NAME = 'SDA'
FORMAT_VERSION = '1.1'


class SDAFile(h5py.File):  # pylint: disable=too-many-ancestors
    """The main entry point for interacting with the SDA format.
    This file object contains most variables and methods needed
    for using the file. Note that the data is provided in a 'raw'
    format, so the user is responsible for interprating the data
    in a manner useful to them. Specifically note that some of the
    pre-defined data-type the SDA library uses are matlab functions
    and may not be compatible with python. This issue may be
    addressed at a later time.
    """
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


class MetaHolder(type(h5py.Group), type(HasTraits)):  # Oh dear...
    pass


class Record(h5py.Group, HasTraits):
    """The base class for SDA records. Contains logic for enforcing
    constraints on its members."""
    __metaclass__ = MetaHolder
    def __init__(self, record_type):
        self.record_type = record_type
#
#
# class Record(object):
#     def __init__(self):
#         pass
#
#
# class Numeric(Record):
#     """Numeric arrays of arbitrary size/dimension."""
#     def __init__(self):
#         super(Numeric, self).__init__()
#
#
# class Logical(Record):
#     """Logical arays of arbitrary size/dimension."""
#     def __init__(self):
#         super(Logical, self).__init__()
#
#
# class Character(Record):
#     """Character arrays of arbitrary size/dimension."""
#     def __init__(self):
#         super(Character, self).__init__()
#
#
# # This may need to be removed.
# class Function(Record):
#     """MATLAB function handles."""
#     def __init__(self):
#         super(Function, self).__init__()
#
#
# class Cell(Record):
#     """Cell arrays of arbitrary size/dimension."""
#     def __init__(self):
#         super(Cell, self).__init__()
#
#
# class Structure(Record):
#     """Structured data."""
#     def __init__(self):
#         super(Structure, self).__init__()
#
#
# class Structures(Record):
#     """Structured data array."""
#     def __init__(self):
#         super(Structures, self).__init__()
#
#
# class Object(Record):
#     """Custom MATLAB object."""
#     def __init__(self):
#         super(Object, self).__init__()
#
#
# class Objects(Record):
#     """Custom MATLAB object array."""
#     def __init__(self):
#         super(Objects, self).__init__()
#
#
# class File(Record):
#     """File stored inside an archive."""
#     def __init__(self):
#         super(File, self).__init__()
#
#
# class Split(Record):
#     """File split across multiple archives."""
#     def __init__(self):
#         super(Split, self).__init__()
