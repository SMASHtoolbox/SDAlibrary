sandia-data-archive
===================

Tools for reading, writing, altering, and inspecting Sandia Data Archive (SDA)
files.

.. image:: https://api.travis-ci.org/enthought/sandia-data-archive.png?branch=master
   :target: https://travis-ci.org/enthought/sandia-data-archive
   :alt: Build status

.. image:: https://ci.appveyor.com/api/projects/status/fbg3ut4bggrevalf/branch/master?svg=true
   :target: https://ci.appveyor.com/project/EnthoughtOSS/sandia-data-archive
   :alt: Build status (Windows)

.. image:: https://coveralls.io/repos/github/enthought/sandia-data-archive/badge.svg?branch=master
   :target: https://coveralls.io/github/enthought/sandia-data-archive?branch=master
   :alt: Coverage status



Installation
------------

The source is hosted on GitHub at
https://github.com/enthought/sandia-data-archive. Releases are available
on the `Python package index <https://pypi.python.org/pypi/sdafile>`_.

::
    pip install sdafile


Installation from source
------------------------

After downloading the source from GitHub, issue the following command from the
command line within the ``sandia-data-archive``
directory

:: 
    python setup.py install

To install the package in development mode, instead issue the command

::
    python setup.py develop


Dependencies
------------

- `H5Py <http://www.h5py.org>`_
- `NumPy <http://www.numpy.org>`_
- `SciPy <http://www.scipy.org>`_
- `Pandas <http://pandas.pydata.org>`_


License
-------
`BSD3 <LICENSE>`_
