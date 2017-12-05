.. default-domain:: py

.. py:currentmodule:: sdafile.sda_file

Quickstart
==========

The ``sdafile`` package enables interacting with Sandia Data Archive format
files via the :class:`SDAFile` class. This class has a lightweight interface
for interacting with SDA files, backed by `h5py <http://www.h5py.org>`_.

To open an SDA file, instantiate :class:`SDAFile` with the file name, and
the file access mode. ::

    from sdafile import SDAFile
    sda_file = SDAFile('example.sda', 'w')

In this case, we're creating a new file named ``example.sda`` in write mode
(``'w'``). If a file exists with this name, it will be overwritten. To open a
file for reading or appending, use file modes ``'r'`` or ``'a'``, respectively.

Data can be added to the archive via the :meth:`~SDAFile.insert` method.
This method accepts "primitive" data: numeric, boolean, and string scalars,
numeric and boolean arrays (including ``scipy.sparse`` arrays) of arbitrary
shape and size; and "composite" data, lists, dictionaries, or object arrays
containing other primitive or composite data. ::

    sda_file.insert("example 1", np.arange(10), "optional description")
    sda_file.insert("example 2", ["a string", False, [3, 4, 5]])
    sda_file.insert("example 3", {"T": True, "F": False})

To list the labels, use the :meth:`~SDAFile.labels` method. ::

    >>> sda_file.labels()
    ['example 1', 'example 2', 'example 3']

To get more detailed information, try :meth:`~SDAFile.probe`.

Data can be retrieved via :meth:`~SDAFile.extract`. ::

    >>> sda_file.extract("example 1")
    array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])

    >>> sda_file.extract("example 2")
    ['a string', False, [3, 4, 5]]

    >>> sda_file.extract("example 3")
    {'F': False, 'T': True}

To remove records, use :meth:`~SDAFile.remove`. To replace records,
:meth:`~SDAFile.replace`. ::

    >>> sda_file.remove("example 3")
    >>> sda_file.labels()
    ['example 1', 'example 2']

    >>> sda_file.replace("example 1", np.zeros(5, dtype=float))
    >>> sda_file.extract("example 1")
    np.array([0., 0., 0., 0., 0.])

The SDA format was designed with MATLAB in mind, and can store MATLAB objects
as ``object`` records.  These records cannot be written from Python, but they
can be extracted (as dictionaries) and replaced. Given such a record, the
:meth:`~SDAFile.update_object` can be used to update its contents. ::

    record = different_sda_file.extract("some object record")
    record['Some parameter'] = 10
    different_sda_file.update_object("some object record", record)

Similarly, the :meth:`~SDAFile.update_objects` method is used to update
``objects`` records.
