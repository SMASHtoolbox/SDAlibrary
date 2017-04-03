import os

import h5py


class SDAFile(h5py.File):
    """An SDA file object. Wrapper for the h5py.File
    object. Also functions as a top level group."""
    def __init__(self, archive_name, mode='r'):
        super(SDAFile, self).__init__(archive_name, mode)

    def __repr__(self):
        return '<SDA file "{}" (mode {})>'.format(self.filename, self.mode)

    def __str__(self):
        return repr(self)

    def _get_attrs(self):
        return self.keys()


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
