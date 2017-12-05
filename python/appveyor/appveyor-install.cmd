rem install python packages
pip install --cache-dir C:/egg_cache packaging
pip install --cache-dir C:/egg_cache nose
pip install --cache-dir C:/egg_cache coverage==3.7.1
pip install --cache-dir C:/egg_cache h5py
pip install --cache-dir C:/egg_cache pandas
pip install --cache-dir C:/egg_cache scipy
rem Work around bug in babel 2.0: see mitsuhiko/babel#174
pip install --cache-dir C:/egg_cache babel==1.3
pip install --cache-dir C:/egg_cache Sphinx

rem install sdafile
python setup.py develop
