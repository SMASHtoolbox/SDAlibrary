""" Utility functions and data.

The functions in the module work directly on data and metadata. In order to
make this easy to write and test, functionality that requires direct
interaction with HDF5 are not included here.

"""

from datetime import datetime
import re
import string
import time

import numpy as np

from .exceptions import BadSDAFile


# DD-MMM-YYYY HH:MM:SS
# MATLAB code uses 'datestr' to create this. HH:MM:SS is optional if all zero.
# This variant is DATE_FORMAT_SHORT.
DATE_FORMAT = "%d-%b-%Y %H:%M:%S"
DATE_FORMAT_SHORT = "%d-%b-%Y"

# Record groups.
SIMPLE_RECORD_TYPES = ('character', 'logical', 'numeric', 'file')
SUPPORTED_RECORD_TYPES = (
    'character', 'file', 'logical', 'numeric', 'cell', 'structure',
    'structures', 'object', 'objects',
)


# Regular expression for version string
VERSION_1_RE = re.compile(r'1\.(?P<sub>\d+)')


# Type codes for unsupported numeric types
UNSUPPORTED_NUMERIC_TYPE_CODES = {
    'G',  # complex256
    'g',  # float128
    'e',  # float16
}

# Empty values for supported types
EMPTY_FOR_TYPE = {
    'numeric': np.nan,
    'character': '',
    'file': b'',
    'logical': np.array([], dtype=bool),
    'cell': [],
    'structure': {}
}

# Equivalent record types for reading
STRUCTURE_EQUIVALENT = {'structure', 'object'}
CELL_EQUIVALENT = {'cell', 'objects', 'structures'}


# Cell label template and generator function
CELL_LABEL_TEMPLATE = "element {}"
cell_label = CELL_LABEL_TEMPLATE.format


def are_record_types_equivalent(rt1, rt2):
    """ Determine if record types are equivalent with respect to reading """
    if rt1 == rt2:
        return True

    if rt1 in STRUCTURE_EQUIVALENT and rt2 in STRUCTURE_EQUIVALENT:
        return True

    if rt1 in CELL_EQUIVALENT and rt2 in CELL_EQUIVALENT:
        return True

    return False


def are_signatures_equivalent(sig1, sig2):
    """ Verify if data signatures are equivalent.

    Parameters
    ----------
    sig1, sig2 :
        Data or group signatures returned by unnest or unnest_record.

    """
    if len(sig1) != len(sig2):
        return False

    for item1, item2 in zip(sig1, sig2):
        key1, rt1 = item1
        key2, rt2 = item2
        if key1 != key2:
            return False

        if not are_record_types_equivalent(rt1, rt2):
            return False

    return True


def error_if_bad_attr(h5file, attr, is_valid):
    """ Raise BadSDAFile error if h5file has a bad SDA attribute.

    This assumes that the attr is stored as bytes. The passed ``is_valid``
    function should accept the value as a string.

    """
    name = h5file.filename
    try:
        value = h5file.attrs[attr]
    except KeyError:
        msg = "File '{}' does not contain '{}' attribute".format(name, attr)
        raise BadSDAFile(msg)
    else:
        value = value.decode('ascii')
        if not is_valid(value):
            msg = "File '{}' has invalid '{}' attribute".format(name, attr)
            raise BadSDAFile(msg)


def error_if_bad_header(h5file):
    """ Raise BadSDAFile if SDA header attributes are missing or invalid. """
    # FileFormat flag
    error_if_bad_attr(h5file, 'FileFormat', is_valid_file_format)

    # FormatVersion flag
    error_if_bad_attr(h5file, 'FormatVersion', is_valid_format_version)

    # Writable flag
    error_if_bad_attr(h5file, 'Writable', is_valid_writable)

    # Created flag
    error_if_bad_attr(h5file, 'Created', is_valid_date)

    # Updated flag
    error_if_bad_attr(h5file, 'Updated', is_valid_date)


def error_if_not_writable(h5file):
    """ Raise an IOError if an SDAFile indicates 'Writable' as 'no'. """
    writable = h5file.attrs.get('Writable')
    if writable == b'no':
        msg = "File '{}' is not writable".format(h5file.filename)
        raise IOError(msg)


def get_date_str(dt=None):
    """ Get a valid date string from a datetime, or current time. """
    if dt is None:
        dt = datetime.now()
    if dt.hour == dt.minute == dt.second == 0:
        fmt = DATE_FORMAT_SHORT
    else:
        fmt = DATE_FORMAT
    date_str = dt.strftime(fmt)
    return date_str


def get_empty_for_type(record_type):
    """ Get the empty value for a record.

    Raises
    ------
    ValueError if ``record_type`` does not have an empty entry.

    """
    try:
        return EMPTY_FOR_TYPE[record_type]
    except KeyError:
        msg = "Record type '{}' cannot be empty".format(record_type)
        raise ValueError(msg)


def is_simple(record_type):
    """ Check if record type is simple (primitive or 'file'). """
    return record_type in SIMPLE_RECORD_TYPES


def is_supported(record_type):
    """ Check if record type is supported. """
    return record_type in SUPPORTED_RECORD_TYPES


def is_valid_date(date_str):
    """ Check date str conforms to DATE_FORMAT or DATE_FORMAT_SHORT. """
    try:
        time.strptime(date_str, DATE_FORMAT)
    except ValueError:
        try:
            time.strptime(date_str, DATE_FORMAT_SHORT)
        except ValueError:
            return False
    return True


def is_valid_file_format(value):
    """ Check that file format is equivalent to 'SDA' """
    return value == 'SDA'


def is_valid_format_version(value):
    """ Check that version is '1.X' for X <= 1 """
    m = VERSION_1_RE.match(value)
    if m is None:
        return False
    return 0 <= int(m.group('sub')) <= 1


def is_valid_matlab_field_label(label):
    """ Check that passed string is a valid MATLAB field label """
    if not label.startswith(tuple(string.ascii_letters)):
        return False
    VALID_CHARS = set(string.ascii_letters + string.digits + "_")
    return set(label).issubset(VALID_CHARS)


def is_valid_writable(value):
    """ Check that writable flag is 'yes' or 'no' """
    return value == 'yes' or value == 'no'


def set_encoded(dict_like, **attrs):
    """ Encode and insert values into a dict-like object. """
    encoded = {
        attr: value.encode('ascii') if isinstance(value, str) else value
        for attr, value in attrs.items()
    }
    dict_like.update(encoded)


def get_decoded(dict_like, *attrs):
    """ Retrieve decoded values from a dict-like object if they exist.

    If no attrs are passed, all values are retrieved.

    """
    # Filter for existing
    if len(attrs) == 0:
        items = dict_like.items()
    else:
        items = [
            (attr, dict_like[attr]) for attr in attrs if attr in dict_like
        ]
    return {
        attr: value.decode('ascii') if isinstance(value, bytes) else value
        for attr, value in items
    }


def get_record_type(dict_like):
    """ Retrived decoded record type from a dict-like object. """
    return get_decoded(dict_like, 'RecordType').get('RecordType')


def unnest(data, registry):
    """ Unnest data.

    Parameters
    ----------
    data :
        Data to unnest
    registry : InserterRegistry
        Registry used to look up inserters

    Returns
    -------
    record_signature :
        A tuple of (path, record_type) tuples where each component of the data
        is identified in the path.

    """
    record_type = getattr(registry.get_inserter(data), 'record_type', None)
    items = [('', record_type, data)]
    for parent, record_type, obj in items:
        if record_type in SIMPLE_RECORD_TYPES:
            continue
        if are_record_types_equivalent(record_type, 'structure'):
            sub_items = sorted(obj.items())
        elif are_record_types_equivalent(record_type, 'cell'):
            sub_items = [
                (cell_label(i), sub_obj)
                for i, sub_obj in enumerate(obj, start=1)
            ]
        for key, sub_obj in sub_items:
            path = "/".join((parent, key)).lstrip("/")
            sub_record_type = getattr(
                registry.get_inserter(sub_obj), 'record_type', None
            )
            items.append((path, sub_record_type, sub_obj))
    return tuple(item[:2] for item in items)


def unnest_record(grp):
    """ Unnest a record group stored on file.

    Parameters
    ----------
    grp : h5py.Group
        The group to unnest.

    Returns
    -------
    record_signature :
        A tuple of (path, record_type) tuples where each component of the group
        is identified in the path.

    """
    record_type = get_record_type(grp.attrs)
    items = [('', record_type, grp)]
    for parent, record_type, obj in items:
        if record_type not in SIMPLE_RECORD_TYPES:
            for key in sorted(obj.keys()):
                path = "/".join((parent, key)).lstrip("/")
                sub_obj = obj[key]
                sub_record_type = get_record_type(sub_obj.attrs)
                items.append((path, sub_record_type, sub_obj))
    return tuple(item[:2] for item in items)


def validate_structures(data, registry):
    """ Validate that passed data is suitable to be a 'structures' record. """
    # Signatures must be homogeneous.
    signatures = set(
        unnest(sub_data, registry) for sub_data in np.ravel(data)
    )
    if len(signatures) > 1:
        msg = "Data cells are not homogenous"
        raise ValueError(msg)

    # The top-most record must be a structure record
    sig = signatures.pop()
    record_type = sig[0][1]
    if record_type != 'structure':
        msg = "Data does not contain structure records"
        raise ValueError(msg)

    return sig


def update_header(attrs):
    """ Update timestamp and version to 1.1 in a header. """
    set_encoded(
        attrs,
        FormatVersion='1.1',
        Updated=get_date_str(),
    )


def write_header(attrs):
    """ Write default, encoded header values to dict-like ``attrs``. """
    date_str = get_date_str()
    set_encoded(
        attrs,
        FileFormat='SDA',
        FormatVersion='1.1',
        Writable='yes',
        Created=date_str,
        Updated=date_str,
    )
