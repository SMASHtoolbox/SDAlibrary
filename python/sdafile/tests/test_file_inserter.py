import numpy as np
from sdafile.file_inserter import FileInserter
from sdafile.testing import InserterTestCase, temporary_file


class TestFileInserter(InserterTestCase):

    def setUp(self):
        InserterTestCase.setUp(self)
        self.grp_attrs = dict(
            RecordType='file',
            Empty='no',
        )
        self.ds_attrs = dict(
            RecordType='numeric',
            Empty='no',
            Complex='no',
            Sparse='no',
        )

    def tearDown(self):
        del self.grp_attrs
        del self.ds_attrs
        InserterTestCase.tearDown(self)

    def test_file_inserter_binary(self):
        with temporary_file() as file_path:
            contents = b'01'
            with open(file_path, 'wb') as f:
                f.write(contents)

            with open(file_path, 'rb') as f:
                expected = np.array([48, 49], np.uint8).reshape(2, 1)
                self.assertSimpleInsert(
                    FileInserter,
                    f,
                    self.grp_attrs,
                    self.ds_attrs,
                    expected,
                )

    def test_file_inserter_ascii(self):
        with temporary_file() as file_path:
            contents = b'01'
            with open(file_path, 'wb') as f:
                f.write(contents)

            with open(file_path, 'r') as f:
                expected = np.array([48, 49], np.uint8).reshape(2, 1)
                self.assertSimpleInsert(
                    FileInserter,
                    f,
                    self.grp_attrs,
                    self.ds_attrs,
                    expected,
                )

    def test_file_inserter_empty(self):
        with temporary_file() as file_path:
            with open(file_path, 'rb') as f:

                self.grp_attrs['Empty'] = self.ds_attrs['Empty'] = 'yes'
                self.assertSimpleInsert(
                    FileInserter,
                    f,
                    self.grp_attrs,
                    self.ds_attrs,
                    expected=None,
                )
