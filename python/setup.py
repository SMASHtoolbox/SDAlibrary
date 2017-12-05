import os

from setuptools import setup, find_packages

# Get version from version.py.
version_filename = os.path.join("sdafile", "version.py")
with open(version_filename) as version_file:
    version_py_locals = {}
    exec(version_file.read(), version_py_locals)
    version = version_py_locals["version"]


install_requires = [
    "h5py",
    "scipy",
    "pandas",
    "numpy",
    "packaging",
]


setup(
    name="sdafile",
    version=version,
    packages=find_packages(),
    author="Christopher L. Farrow",
    author_email="cfarrow@enthought.com",
    maintainer="Sandia National Laboratories",
    url="https://github.com/enthought/sandia-data-archive",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: OS Independent",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Programming Language :: Python",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
    ],
    description=(
        'Tools for reading, writing, altering, and inspecting Sandia Data '
        'Archive (SDA) files.'
    ),
    install_requires=install_requires,
    license='BSD',
    platforms=["Windows", "Linux", "Mac OS-X", "Unix", "Solaris"],
    zip_safe=True,
)
