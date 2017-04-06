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
    
    # TODO: Implement Type checking for each record










# Record Defintions

class Numeric:
    def __init__(self):
        pass


class Logical:
    def __init__(self):
        pass


class Character:
    def __init__(self):
        pass


class Function:
    def __init__(self):
        pass
        

class Cell:
    def __init__(self):
        pass


class Structure:
    def __init__(self):
        pass
        

class Structures:
    def __init__(self):
        pass
        
        
class Object:
    def __init__(self):
        pass


class Objects:
    def __init__(self):
        pass


class File:
    def __init__(self):
        pass


class Split:
    def __init__(self):
        pass


