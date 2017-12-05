import unittest

from packaging.version import parse

import sdafile
from sdafile.version import version


class Version(unittest.TestCase):

    def test_imports(self):
        self.assertEqual(sdafile.__version__, version)

    def test_pep_440(self):
        # Raises InvalidVersion if version does not conform to pep440
        parse(version)
