"""
:mod:`pysda` -- Python implementation of the SDA Library
===========================================================

Python implementation of the SDA Library

.. module::
   :synopsis: Python implementation of the SDA Library
"""

import h5py


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
        self.file_format = self.attrs['FileFormat']
        self.format_verion = self.attrs['FormatVersion']
        self.created = self.attrs['Created']
        self.updated = self.attrs['Updated']
        self.writable = self.attrs['Writable']

    # TODO: Implement Type checking for each record

# Record Defintions


class Record:
    def __init__(self):
        pass


class Numeric(Record):
    """Numeric arrays of arbitrary size/dimension."""
    def __init__(self):
        self.record_type = None
        self.empty = None
        self.description = None
        self.deflate = None
        self.complex = None
        self.sparse = None
        self.command = None
        pass


class Logical(Record):
    """Logical arays of arbitrary size/dimension."""
    def __init__(self):
        pass


class Character(Record):
    """Character arrays of arbitrary size/dimension."""
    def __init__(self):
        pass


# This may need to be removed.
class Function(Record):
    """MATLAB function handles."""
    def __init__(self):
        pass


class Cell(Record):
    """Cell arrays of arbitrary size/dimension."""
    def __init__(self):
        pass


class Structure(Record):
    """Structured data."""
    def __init__(self):
        pass


class Structures(Record):
    """Structured data array."""
    def __init__(self):
        pass


class Object(Record):
    """Custom MATLAB object."""
    def __init__(self):
        pass


class Objects(Record):
    """Custom MATLAB object array."""
    def __init__(self):
        pass


class File(Record):
    """File stored inside an archive."""
    def __init__(self):
        pass


class Split(Record):
    """File split across multiple archives."""
    def __init__(self):
        pass
