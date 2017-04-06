import os

import h5py

import pysda
from pysda.recordtypes import (Numeric, Logical, Character, Function, Cell,
                               Structure, Structures, Object, Objects)



RECORDTYPES = {'Numeric': Numeric, 'Logical': Logical, 'Character': Character,
               'Function': Function, 'Cell': Cell}


class SDAFile(h5py.File):
    """SDA file object. Wrapper for the h5py.File
    object. Also functions as a top level group."""
    def __init__(self, archive_name, mode='r'):
        super(SDAFile, self).__init__(archive_name, mode)

    def __repr__(self):
        return '<SDA file "{}" (mode {})>'.format(self.filename, self.mode)

    def write(self, file_name):
        new_file = SDAFile(file_name, mode='w-')
        for key, val in self.items():
            self.copy(val, new_file['/'])
        new_file.close()










def _cast_data(data):
    data_type = data.attrs['RecordType']
    data = RECORDTYPES[data_type](data)
    return data


# TODO: Move this somewhere else.
def probe_file(archive_name):
    archive = SDAFile(archive_name, mode='r')
    attrs = archive.attrs
    keys = archive.keys()
    probe_string = '\n' + os.path.abspath(archive_name) + '\n\n'
    for key, value in attrs.items():
        probe_string += _format_file_attr(key, value)
    probe_string += '-'*100 + '\n'
    probe_string += _formatted_group_output('Label', 'Type', 'Description')
    probe_string += '-'*100 + '\n'
    for key, value in archive.items():
        probe_string += _formatted_group_output(key, get_record_type(key, archive), get_description(key, archive))
    print probe_string


def _format_file_attr(attr_key, attr_value):
    return '{:>15}:  \'{}\'\n'.format(attr_key, attr_value)


def _formatted_group_output(label, record_type, description):
    return '{:<30}{:<15}{:<50}\n'.format(label, record_type, description)


def get_description(key, archive):
    group = archive[key]
    description = group.attrs['Description']
    return description


def get_record_type(key, archive):
    group = archive[key]
    record_type = group.attrs['RecordType']
    return record_type
