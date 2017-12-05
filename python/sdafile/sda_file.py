""" Implementation of ``SDAFile`` for working with SDA files.

The SDA format was designed to be universal to facilitate data sharing across
multiple languages. It supports reading and updating all record types, except
*function* records. It support writing *numeric*, *logical*, *cell*, and
*structure* records.

"""

from contextlib import contextmanager
from functools import partial
import os
import os.path as op
import re
import shutil
import tempfile

import h5py
import numpy as np

from .extract import extract
from .record_inserter import InserterRegistry
from .utils import (
    are_signatures_equivalent, error_if_bad_header, error_if_not_writable,
    get_decoded, is_valid_writable, set_encoded, unnest, unnest_record,
    update_header, validate_structures, write_header,
)


WRITE_MODES = ('w', 'w-', 'x', 'a')


class SDAFile(object):
    """ Read, write, inspect, and manipulate Sandia Data Archive files.

    This supports version 1.1 of the Sandia Data Archive format.

    """

    def __init__(self, name, mode='a', **kw):
        """ Open an SDA file for reading, writing, or interrogation.

        Parameters
        ----------
        name : str
            The name of the file to be loaded or created.
        mode : str
            r         Read-only, file must exist
            r+        Read/write, file must exist
            w         Create file, truncate if exists
            w- or x   Create file, fail if exists
            a         Read/write if exists, create otherwise (default)
        kw :
            Key-word arguments that are passed to the underlying HDF5 file. See
            h5py.File for options.

        """
        file_exists = op.isfile(name)
        self._mode = mode
        self._filename = name
        self._kw = kw
        self._registry = InserterRegistry()

        # Check existence
        if mode in ('r', 'r+') and not file_exists:
            msg = "File '{}' does not exist".format(name)
            raise IOError(msg)

        # Check the header when mode requires the file to exist
        if mode in ('r', 'r+') or (file_exists and mode == 'a'):
            with self._h5file('r') as h5file:
                error_if_bad_header(h5file)

            # Check that file is writable when mode will write to file.
            if mode != 'r':
                with self._h5file('a') as h5file:
                    error_if_not_writable(h5file)

        # Create the header if this is a new file
        if mode in ('w', 'w-', 'x') or (not file_exists and mode == 'a'):
            with self._h5file(mode) as h5file:
                write_header(h5file.attrs)

    # File properties

    @property
    def name(self):
        """ File name on disk. """
        return self._filename

    @property
    def mode(self):
        """ Mode used to open file. """
        return self._mode

    # Format attrs

    @property
    def FileFormat(self):
        """ The 'FileFormat' file attribute. """
        return self._get_attr('FileFormat')

    @property
    def FormatVersion(self):
        """ The format version from the SDA file. """
        return self._get_attr('FormatVersion')

    @property
    def Writable(self):
        """ The 'Writable' flag from the SDA file. """
        return self._get_attr('Writable')

    @Writable.setter
    def Writable(self, value):
        if self._mode not in WRITE_MODES:
            raise ValueError("File is not writable.")
        if not is_valid_writable(value):
            raise ValueError("Must be 'yes' or 'no'")
        with self._h5file('r+') as h5file:
            set_encoded(h5file.attrs, Writable=value)

    @property
    def Created(self):
        """ The time the file was created. """
        return self._get_attr('Created')

    @property
    def Updated(self):
        """ The time the file was last updated. """
        return self._get_attr('Updated')

    # Public
    def describe(self, label, description=''):
        """ Change the description of a data entry.

        Parameters
        ----------
        label : str
            The data label.
        description : str
            A description to accompany the data

        Raises
        ------
        ValueError if the label contains invalid characters
        ValueError if the label does not exist

        """
        self._validate_can_write()
        self._validate_labels(label, must_exist=True)
        with self._h5file('r+') as h5file:
            set_encoded(h5file[label].attrs, Description=description)
            update_header(h5file.attrs)

    def extract(self, label):
        """ Extract data from an SDA file.

        Parameters
        ----------
        label : str
            The data label.

        Returns
        -------
        data : object
            Archive data associated with the label.

        Notes
        -----
        Sparse numeric data is extracted as
        :class:`coo_matrix<scipy:scipy.sparse.coo_matrix>`. This format does
        not support all numpy operations.

        Raises
        ------
        ValueError if the label contains invalid characters
        ValueError if the label does not exist

        """
        self._validate_labels(label, must_exist=True)
        with self._h5file('r') as h5file:
            return extract(h5file, label)

    def extract_to_file(self, label, path, overwrite=False):
        """ Extract a file record to file.

        Parameters
        ----------
        label : str
            Label of the file record.
        path : str
            The path to which the file is to be written.
        overwrite : bool, optional
            Unless specified as True, an existing file with the chosen name
            will not be overwritten by this method.

        Raises
        ------
        IOError if `overwrite` is False and the destintation file exists.

        """

        if op.exists(path) and not overwrite:
            raise IOError("File '{}' exists. Will not overwrite.".format(path))
        self._validate_labels(label, must_exist=True)

        # Check that archive is a file archive
        record_type = self._get_attr('RecordType', root=label)
        if record_type != 'file':
            raise ValueError("'{}' is not a file record".format(label))

        with open(path, 'wb') as f:
            f.write(self.extract(label))

    def insert(self, label, data, description='', deflate=0,
               as_structures=False):
        """ Insert data into an SDA file.

        Parameters
        ----------
        label : str
            The data label.
        data :
            The data to insert. See the notes below.
        description : str, optional
            A description to accompany the data
        deflate : int, optional
            An integer value from 0 to 9, specifying the compression level to
            be applied to the stored data.
        as_record : bool, optional
            If specified, data that is storable as a cell record and has
            homogenous cells will be stored as a "structures" record. Note that
            this does not extend to nested cell records.

        Raises
        ------
        ValueError if the data is of an unsupported type
        ValueError if the label contains invalid characters
        ValueError if the label exists
        ValueError if `as_structures` is True and the data cannot be stored as
        a structures record.

        Notes
        -----
        This stores specific data types as described here.

        sequences :
            Lists, tuples, and anything else that identifies as a
            collections.abc.Sequence are stored as 'cell' records, no matter
            the contents.

        dicts :
            Dictionaries are stored as 'structure' records.

        numpy arrays :
            If the dtype is a supported numeric type, then a numpy array is
            stored as a 'numeric' record. Arrays of 'bool' type are stored as
            'logical' records.  Arrays of characters (dtype 'S1') are stored as
            'character' records. Object and string arrays are stored as 'cell'
            records.

        sparse arrays (:class:`coo_matrix<scipy:scipy.sparse.coo_matrix>`) :
            These are stored as 'numeric' records if the dtype is a type
            supported for numeric numpy arrays.

        strings :
            Strings are stored as 'character' records. An attempt will be
            made to convert the input to ascii encoded bytes, no matter the
            underlying encoding. This may result in an encoding exception if
            the input cannot be ascii encoded.

        non-string scalars :
            Non-string scalars are stored as 'numeric' if numeric, or 'logical'
            if boolean.

        file-like :
            The contents of a file-like objects (with a 'read' method) are
            stored as 'file' records.

        other :
            Arrays of characters are not supported. Convert to a string.
            Object arrays are not supported. Cast to another dtype or turn into
            a list.

        Anything not listed above is not (intentionally) supported.

        See Also
        --------
        insert_from_file : Insert contents of a named file.

        """
        self._validate_can_write()
        self._validate_labels(label, can_exist=False)
        if not isinstance(deflate, (int, np.integer)) or not 0 <= deflate <= 9:
            msg = "'deflate' must be an integer from 0 to 9"
            raise ValueError(msg)
        cls = self._registry.get_inserter(data)
        if cls is None:
            msg = "{!r} is not a supported type".format(data)
            raise ValueError(msg)

        inserter = cls(label, data, deflate, self._registry)

        if as_structures:
            if inserter.record_type != 'cell':
                msg = "Data cannot be stored as a 'structures' record."
                raise ValueError(msg)

            validate_structures(data, self._registry)

            # Tell the inserter to use the 'structures' record type
            inserter.record_type = 'structures'

        with self._h5file('r+') as h5file:
            try:
                inserter.insert(h5file, description)
            except Exception:
                # Do not leave things in an invalid state
                if label in h5file:
                    del h5file[label]
                raise
            else:
                update_header(h5file.attrs)

    def insert_from_file(self, path, description='', deflate=0):
        """ Insert the contents of a file as a file record.

        Parameters
        ----------
        path : str
            The path to the file. The basename of the path will be used as the
            record label.
        description : str, optional
            A description to accompany the data
        deflate : int, optional
            An integer value from 0 to 9, specifying the compression level to
            be applied to the stored data.

        Returns
        -------
        label : str
            The label under which the file was stored.

        See Also
        --------
        insert : Insert data into the archive

        """
        if not op.isfile(path):
            raise ValueError("File '{}' does not exist".format(path))

        label = op.basename(path)
        with open(path, 'rb') as f:
            self.insert(label, f, description, deflate)
        return label

    def labels(self):
        """ Get data labels from the archive.

        Returns
        -------
        labels : list of str
            Labels from the archive.

        """
        with self._h5file('r') as h5file:
            return list(h5file.keys())

    def remove(self, *labels):
        """ Remove specified records from the archive.

        This cannot be undone.

        """
        self._validate_can_write()
        self._validate_labels(labels, must_exist=True)

        # Create a new file so space is actually freed
        def _copy_visitor(path, source, destination, labels):
            """ Visitor that copies data from source to destination """

            # Skip paths corresponding to excluded labels
            if path.split('/')[0] in labels:
                return

            # Copy everything else
            source_obj = source[path]
            if isinstance(source_obj, h5py.Group):
                dest_obj = destination.create_group(path)
            else:
                ds = source_obj
                dest_obj = destination.create_dataset(
                    path,
                    data=source_obj[()],
                    chunks=ds.chunks,
                    maxshape=ds.maxshape,
                    compression=ds.compression,
                    compression_opts=ds.compression_opts,
                    scaleoffset=ds.scaleoffset,
                    shuffle=ds.shuffle,
                    fletcher32=ds.fletcher32,
                    fillvalue=ds.fillvalue,
                )

            dest_obj.attrs.update(source_obj.attrs)

        pid, destination_path = tempfile.mkstemp()
        os.close(pid)
        with h5py.File(destination_path, 'w') as destination:
            with self._h5file('r') as source:
                destination.attrs.update(source.attrs)
                source.visit(
                    partial(
                        _copy_visitor,
                        source=source,
                        destination=destination,
                        labels=set(labels),

                    )
                )
            update_header(destination.attrs)
        shutil.move(destination_path, self._filename)

    def probe(self, pattern=None):
        """ Summarize the state of the archive

        This requires the pandas package.

        Parameters
        ----------
        pattern : str or None, optional
            A search pattern (python regular expression) applied to find
            archive labels of interest. If None, all labels are selected.

        Returns
        -------
        summary : :class:`DataFrame<pandas:pandas.DataFrame>`
            A table summarizing the archive.

        """
        from pandas import DataFrame
        labels = self.labels()
        if pattern is not None:
            regex = re.compile(pattern)
            labels = [
                label for label in labels if regex.match(label) is not None
            ]

        summary = []
        with self._h5file('r') as h5file:
            for label in labels:
                g = h5file[label]
                attrs = get_decoded(g.attrs)
                if label in g:
                    attrs.update(get_decoded(g[label].attrs))
                attrs['label'] = label
                summary.append(attrs)

        cols = [
            'label', 'RecordType', 'Description', 'Empty', 'Deflate',
            'Complex', 'ArraySize', 'Sparse', 'RecordSize', 'Class',
            'FieldNames', 'Command',
        ]
        return DataFrame(summary, columns=cols).set_index('label').fillna('')

    def replace(self, label, data):
        """ Replace an existing dataset.

        Parameters
        ----------
        label : str
            The record label.
        data :
            The data with which to replace the record.

        Notes
        -----
        This is equivalent to removing the data and inserting a new entry using
        the same ``label``, ``description``, and ``deflate`` options.

        """
        self._validate_can_write()
        self._validate_labels(label, must_exist=True)
        with self._h5file('r+') as h5file:
            attrs = get_decoded(h5file[label].attrs, 'Deflate', 'Description')
            del h5file[label]
        self.insert(label, data, attrs['Description'], attrs['Deflate'])

    def update_object(self, label, data):
        """ Update an existing object record.

        Parameters
        ----------
        label : str
            Label of the object record.
        data : dict
            The data with which to replace the object record.

        Notes
        -----
        This is more strict than **replace** in that the intention is to update
        the contents of an 'object' record while preserving the record type.
        The simplest way to make use of this is to *extract* an object record,
        replace some data, and then call this to update the stored record.

        """
        self._validate_can_write()
        self._validate_labels(label, must_exist=True)

        cls = self._registry.get_inserter(data)
        if cls is None:
            msg = "{!r} is not a supported type".format(data)
            raise ValueError(msg)

        record_type = cls.record_type
        if record_type != 'structure':
            raise ValueError("Input data is not a dictionary")

        with self._h5file('r+') as h5file:
            # Check the general structure of the data and file
            grp = h5file[label]
            attrs = get_decoded(grp.attrs)
            if not attrs['RecordType'] == 'object':
                raise ValueError("Record '{}' is not an object".format(label))
            if attrs['Empty'] == 'yes':
                raise ValueError("Cannot update an empty record")
            record_sig = unnest_record(grp)
            data_sig = unnest(data, self._registry)
            if not are_signatures_equivalent(record_sig, data_sig):
                msg = "Data is not compatible with record '{}'"
                raise ValueError(msg.format(label))

            del h5file[label]

        self.insert(label, data, attrs['Description'], int(attrs['Deflate']))

        # Fix the record type and update the header
        with self._h5file('r+') as h5file:
            grp = h5file[label]
            set_encoded(
                grp.attrs,
                RecordType='object',
                Class=attrs['Class'],
            )
            update_header(h5file.attrs)

    def update_objects(self, label, data):
        """ Update an existing objects record.

        Parameters
        ----------
        label : str
            Label of the objects record.
        data : list
            The data with which to replace the objects record.

        Notes
        -----
        This is more strict than **replace** in that the intention is to update
        the contents of an 'objects' record while preserving the record type.
        The simplest way to make use of this is to *extract* an objects record,
        replace some data, and then call this to update the stored record.

        """
        self._validate_can_write()
        self._validate_labels(label, must_exist=True)

        cls = self._registry.get_inserter(data)
        if cls is None:
            msg = "{!r} is not a supported type".format(data)
            raise ValueError(msg)

        record_type = cls.record_type
        if record_type != 'cell':
            raise ValueError("Input data is not a list")

        # To be an 'objects' record, this must look like a 'structures' record.
        data_sig = validate_structures(data, self._registry)

        with self._h5file('r+') as h5file:
            # Check the general structure of the data and file
            grp = h5file[label]
            attrs = get_decoded(grp.attrs)
            if not attrs['RecordType'] == 'objects':
                raise ValueError("Record '{}' is not an objects".format(label))
            if attrs['Empty'] == 'yes':
                raise ValueError("Cannot update an empty record")
            record_sig = unnest_record(grp['element 1'])
            if not are_signatures_equivalent(record_sig, data_sig):
                msg = "Data is not compatible with record '{}'"
                raise ValueError(msg.format(label))

            del h5file[label]

        self.insert(label, data, attrs['Description'], int(attrs['Deflate']))

        # Fix the record type and update the header
        with self._h5file('r+') as h5file:
            grp = h5file[label]
            set_encoded(
                grp.attrs,
                RecordType='objects',
                Class=attrs['Class'],
            )
            update_header(h5file.attrs)

    # Private

    @contextmanager
    def _h5file(self, mode):
        h5file = h5py.File(self._filename, mode, **self._kw)
        try:
            yield h5file
        finally:
            h5file.close()

    def _get_attr(self, attr, root=None):
        """ Get a named atribute as a string """
        with self._h5file('r') as h5file:
            if root is None:
                obj = h5file
            else:
                obj = h5file[root]
            return get_decoded(obj.attrs, attr)[attr]

    def _validate_can_write(self):
        """ Validate file mode and 'Writable' attr allow writing. """
        if self._mode not in WRITE_MODES:
            raise IOError("File is not writable")
        if self.Writable == 'no':
            raise IOError("'Writable' flag is 'no'")

    def _validate_labels(self, labels, can_exist=True, must_exist=False):
        if isinstance(labels, str):
            labels = [labels]
        if len(labels) == 0:
            raise ValueError("Must specify labels")
        for label in labels:
            if '/' in label or '\\' in label:
                msg = r"label cannot contain '/' or '\'"
                raise ValueError(msg)
        with self._h5file('r') as h5file:
            for label in labels:
                label_exists = label in h5file
                if not can_exist and label_exists:
                    msg = "Label '{}' already exists.".format(label)
                    raise ValueError(msg)
                if must_exist and not label_exists:
                    msg = "Label item '{}' does not exist".format(label)
                    raise ValueError(msg)
