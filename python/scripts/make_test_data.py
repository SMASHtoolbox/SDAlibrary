import os.path as op
import argparse

import numpy as np
from scipy import sparse

import sdafile

EXAMPLE_A1 = np.zeros((5, 1), dtype=np.float64)

EXAMPLE_A2 = np.empty((4, 3), dtype=np.complex128)
EXAMPLE_A2.real = 0
EXAMPLE_A2.imag = 1

EXAMPLE_A3 = sparse.eye(5).tocoo()

EXAMPLE_A4 = np.nan

EXAMPLE_B = True

EXAMPLE_C = 'Here is some text'


def make_example_data(filename):

    sda_file = sdafile.SDAFile(filename, 'w')

    ref_path = op.join(op.abspath(
        op.dirname(sdafile.__file__)), 'tests', 'data', 'ReferenceArchive.m'
    )

    sda_file.insert_from_file(
        ref_path, "MATLAB script for generating a reference archive"
    )

    sda_file.insert("example A1", EXAMPLE_A1, "5x1 zeros")

    sda_file.insert("example A2", EXAMPLE_A2, "4x3 imaginary numbers")

    sda_file.insert("example A3", EXAMPLE_A3, "5x5 sparse matrix")

    sda_file.insert("example A4", EXAMPLE_A4, "Empty array")

    sda_file.insert("example B", EXAMPLE_B, "Logical scalar")

    sda_file.insert("example C", EXAMPLE_C, "Some text")

    desc = "Cell array combining examples A1 and A2"
    sda_file.insert("example E", [EXAMPLE_A1, EXAMPLE_A2], desc)

    desc = "Structure combining examples A1 and A2"
    a1a2 = {"A1": EXAMPLE_A1, "A2": EXAMPLE_A2}
    sda_file.insert("example F", a1a2, desc)

    desc = "Structure array combining examples A1 and A2 (repeated)"
    cell = np.array([a1a2, a1a2], dtype=object).reshape(2, 1)
    sda_file.insert("example G", cell, desc, as_structures=True)

    desc = "Cell array of structures combining examples A1-A4"
    a3a4 = {"A3": EXAMPLE_A3, "A4": EXAMPLE_A4}
    cell = np.array([a1a2, a3a4], dtype=object).reshape(2, 1)
    sda_file.insert("example H", cell, desc)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "filename",
        help="The name of the file to create",
        nargs="?",
        default="SDAreference_py.sda",
    )

    args = parser.parse_args()
    make_example_data(args.filename)
