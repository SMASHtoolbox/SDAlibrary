import numpy as np
from scipy.sparse import coo_matrix

from .utils import (
    cell_label, get_decoded, get_empty_for_type, is_simple, is_supported,
)


def extract(h5file, label):
    """ Extract data from an archive.

    Parameters
    ----------
    h5file : h5py.File
        The h5py File containing data
    label : str
        The data label.

    Returns
    -------
    data : object
        Archive data associated with the label.

    """
    grp = h5file[label]
    attrs = get_decoded(grp.attrs)
    return _extract_data_from_group(grp, label, attrs)


def extract_simple(record_type, data, data_attrs):
    """ Extract simple data from its raw storage format.

    Parameters
    -----------
    data : ndarray
        Data extracted from hdf5 dataset storage
    record_type : str
        The simple data type
    data_attrs : dict
        Attributes associated with the stored dataset

    Returns
    -------
    extracted :
        The extracted simple data

    """
    complex_flag = data_attrs.get('Complex', 'no')
    sparse_flag = data_attrs.get('Sparse', 'no')
    shape = data_attrs.get('ArraySize', None)

    if record_type == 'numeric':
        if sparse_flag == 'yes':
            if complex_flag == 'yes':
                extracted = extract_sparse_complex(data, shape.astype(int))
            else:
                extracted = extract_sparse(data)
        elif complex_flag == 'yes':
            extracted = extract_complex(data, shape.astype(int))
        else:
            extracted = extract_numeric(data)
    elif record_type == 'logical':
        extracted = extract_logical(data)
    elif record_type == 'character':
        extracted = extract_character(data)
    elif record_type == 'file':
        extracted = extract_file(data)

    return extracted


def extract_character(data):
    """ Extract 'character' data from uint8 stored form.

    Parameters
    -----------
    data : ndarray
        Array of uint8 ascii encodings

    Returns
    -------
    extracted : str or ndarray
        Reconstructed ascii string. If the input is a row array, then it will
        be converted to a string. Otherwise, it will be returned as an array of
        'S1' dtype.

    """
    # Matlab stores the transpose of 2D arrays. This must be unapplied here.
    data = data.T
    if data.ndim == 2 and data.shape[0] == 1:
        data = data.tobytes().decode('ascii')
    else:
        data = data.view('S1')
    return data


def extract_complex(data, shape):
    """ Extract complex 'numeric' data.

    Parameters
    -----------
    data : ndarray
        2 x N array containing real and imaginary portions of the complex data.
    shape : tuple
        Shape of the extracted array.

    Returns
    -------
    extracted : ndarray
        The extracted complex array.

    """
    extracted = 1j * data[1]
    extracted.real = data[0]
    extracted = extracted.reshape(shape, order='F')
    return reduce_array(extracted)


def extract_file(data):
    """ Extract file data.

    Parameters
    -----------
    data : ndarray
        The file contents as a byte array.

    Returns
    -------
    extracted : bytes
        The data is left alone.

    """
    return data.tobytes()


def extract_logical(data):
    """ Extract 'logical' data from uint8 stored form.

    Parameters
    -----------
    data : ndarray
        Array of uint8 values clipped to 0 or 1

    Returns
    -------
    extracted :
        The extracted boolean or boolean array

    """
    data = np.asarray(data, dtype=bool)
    return reduce_array(data.T)


def extract_numeric(data):
    """ Extract 'numeric' data from stored form.

    Parameters
    -----------
    data : ndarray or scalar
        Array or scalar of numeric data

    Returns
    -------
    data : ndarray or scalar
        The input data

    """
    # Matlab stores the transpose of 2D arrays. This must be unapplied here.
    return reduce_array(data.T)


def extract_sparse(data):
    """ Extract sparse 'numeric' data from stored form.

    Parameters
    -----------
    data : 3xN ndarray
        3xN array containing the rows, columns, and values of a sparse matrix
        in COO form. Note that the row and column arrays must be 1-based to be
        compatible with MATLAB.

    Returns
    -------
    extracted : scipy.sparse.coo_matrix
        The extracted sparse matrix

    """
    row, col, data = data
    # Fix 1-based indexing
    row -= 1
    col -= 1
    return coo_matrix((data, (row, col)))


def extract_sparse_complex(data, shape):
    """ Extract sparse 'numeric' data from stored form.

    Parameters
    -----------
    data : ndarray
        3xN array containing the index, real, and imaginary values of a
        sparse complex data. The index is unraveled and 1-based.
    shape : tuple
        Shape of the extracted array

    Returns
    -------
    extracted : coo_matrix
        The extracted sparse, complex matrix

    """
    index = data[0].astype(np.int64)
    # Fix 1-based indexing
    index -= 1
    data = extract_complex(data[1:], (data.shape[1],))
    row, col = np.unravel_index(index, shape)
    return coo_matrix((data, (row, col)))


def _extract_data_from_group(grp, label, attrs):
    """ Extract data from h5 group. ``label`` is the group label. """

    record_type = attrs['RecordType']
    if not is_supported(record_type):
        msg = "RecordType '{}' is not supported".format(record_type)
        raise ValueError(msg)

    empty = attrs['Empty']
    if empty == 'yes':
        return get_empty_for_type(record_type)

    if is_simple(record_type):
        ds = grp[label]
        data_attrs = get_decoded(ds.attrs)
        return extract_simple(record_type, ds[()], data_attrs)

    if record_type in ('cell', 'structures', 'objects'):
        record_size = attrs['RecordSize'].astype(int)
        nr = np.prod(record_size)
        labels = [cell_label(i) for i in range(1, nr + 1)]
        data = _extract_composite_data(grp, labels)
        if record_size[0] > 1 or len(record_size) > 2:
            data = np.array(
                data, dtype=object,
            ).reshape(record_size, order='F')
    elif record_type in ('structure', 'object'):
        labels = attrs['FieldNames'].split()
        data = _extract_composite_data(grp, labels)
        data = dict(zip(labels, data))
    return data


def _extract_composite_data(grp, labels):
    """ Extract composite data from a Group object with given labels. """
    extracted = []
    for label in labels:
        sub_obj = grp[label]
        attrs = get_decoded(sub_obj.attrs)
        record_type = attrs['RecordType']
        if is_simple(record_type):
            element = extract_simple(record_type, sub_obj[()], attrs)
        else:
            element = _extract_data_from_group(sub_obj, label, attrs)
        extracted.append(element)
    return extracted


def reduce_array(arr):
    """ Reduce a 2d row-array or scalar to 1 or 0 dimensions, respectively. """
    # squeeze leading dimension if this is a MATLAB row array
    if arr.ndim == 2 and arr.shape[0] == 1:
        # if it's a scalar, go all the way
        if arr.shape[1] == 1:
            arr = arr[0, 0]
        else:
            arr = np.squeeze(arr, axis=0)
    return arr
