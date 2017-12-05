.. default-domain:: py

.. py:currentmodule:: sdafile.sda_file

Record Types
============

:class:`SDAFile` accepts various Python data types as records, and can export
most record types as Python data types, be they written from Python or MATLAB.
This section details the specific rules for importing and exporting data from
an SDA file.

Scalars and Arrays
------------------

In MATLAB a scalar is a 1x1 matrix. To support passing data from Python to
MATLAB, Python scalars are stored as 1x1 arrays in an archive. When extracting
a 1x1 matrix from an SDA file into Python, it will be converted to a scalar. 

A similar convention is applied to arrays. There is no "1-D array" in MATLAB.
There are row vectors and column vectors, which are both 2-D. 1-D NumPy arrays
are converted to 2-D before being stored in an SDA file. The NumPy function
:func:`~numpy.atleast_2d` is used for this, which prepends ``1``'s to the
shape of an array until it is 2-D. In other words, NumPy converts a 1-D array
to a row vector. Based on this, row vectors read from an SDA file into Python
are converted to 1-D arrays. Column vectors are not modified.

These conventions may lose information about the data.  Specifically, a 1x1
array inserted in Python will be extracted in Python as a scalar. Likewise, a
1xN array will be extracted as a 1-D array. In many cases, NumPy can handle the
shape changes gracefully (see `broadcasting
<https://docs.scipy.org/doc/numpy-1.13.0/user/basics.broadcasting.html>`_).
However, if you rely on the exact shape of the data, you will need to restore
it on your own.


Numeric Records
---------------

Built-in :class:`float`, :class:`int`, :class:`long` (Python 2), and
:class:`complex` are accepted as ``numeric`` records. Scalars and arrays of
numeric NumPy types are also accepted.  Numeric types that are not specified in
the SDA 1.1 specification (:class:`~numpy.complex256`,
:class:`~numpy.float128`, :class:`~numpy.float16`) are not accepted.

Sparse arrays from ``scipy.sparse`` (with a supported numeric data type) are
also accepted as ``numeric`` records. These are converted to COO form for
insertion, and extracted as ``scipy.sparse.coo.coo_matrix``.

Logical Records
---------------

Built-in :class:`bool` and NumPy :class:`~numpy.bool_` are accepted as
``logical`` records, as are boolean arrays of arbitrary shape.

Character Records
-----------------

Built-in :class:`str`, :class:`unicode` (Python 2), and :class:`bytes` are
accepted as ``character`` records. :class:`str` and :class:`unicode` are
ASCII-encoded before storage, and :class:`bytes` are assumed to be
ASCII-encoded. Errors during encoding or decoding can occur if this assumption
is violated.

Arrays of bytes (dtype ``'S1'``) are also accepted as ``character`` records.
These arrays can have arbitrary shape.

All ``character`` records are stored as arrays (as per the SDA 1.1
specification), and therefore array shape ambiguities like those discussed
above can take place. :class:`str`, :class:`unicode`, :class:`bytes`, 1-D
arrays, and 1xN arrays are always be extracted as :class:`str`. Arrays of bytes
with other shapes are extracted as arrays.  This is provided primarily so that
any character array inserted from MATLAB has a rational representation in
Python.

File Records
------------

Open file-like objects (with a ``read`` method) are accepted as ``file``
records and extracted as :class:`bytes`. :meth:`~SDAFile.insert_from_file``
accepts file on disk and stores it as a ``file`` record, whereas
:meth:`~SDAFile.extract_to_file` writes a ``file`` record to path on disk.

Cell Records
------------

Built-in :class:`list` are accepted as ``cell`` records, provided the list
contents are insertable. These can have arbitrary nesting.

To support ``cell`` records of arbitrary shape, NumPy arrays of objects or
strings are also accepted.

1-D and 1xN ``cell`` records are exported as Python lists. ``cell`` records of
any other shape are exported as object arrays of the appropriate shape.

Structure Records
-----------------

Built-in :class:`dict` are accepted as ``structure`` records, provided the
dictionary contents are insertable. These can have arbitrary nesting.

``structure`` records are extracted as dictionaries.

Object Records
--------------

:class:`SDAFile` provides no support for creating an ``object`` record from
Python. However, :meth:`~SDAFile.update_object` can be used to update an
existing ``object`` record. 

``object`` records are extracted as dictionaries, like structure records.
Information about the MATLAB class corresponding to the object is not
extracted.

Structures Records
------------------

A reasonable equivalent to a ``structures`` record in Python is a list of
homogeneous dictionaries (dictionaries with the same keys and value types).
Such a list (or NumPy array of objects) can be stored as ``structures`` record
by passing the ``as_structures`` keyword to :meth:`~SDAFile.insert`.

``structures`` records are extracted as if they are cell records.

Objects Records
---------------

Like ``object`` records, ``objects`` records cannot be created with
:class:`SDAFile`. However, :meth:`~SDAFile.update_objects` can be used to
update an ``objects`` record.

``objects`` records are extracted as if they are ``cell`` records.
