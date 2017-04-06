import h5py


class SDAFile(h5py.File):
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