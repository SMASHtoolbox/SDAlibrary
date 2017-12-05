import io
import os
import random
import shutil
import unittest

import numpy as np
from numpy.testing import assert_array_equal, assert_equal

from sdafile.exceptions import BadSDAFile
from sdafile.sda_file import SDAFile
from sdafile.testing import (
    BAD_ATTRS, GOOD_ATTRS, MockRecordInserter, TEST_NUMERIC, TEST_CHARACTER,
    TEST_LOGICAL, TEST_SPARSE, TEST_SPARSE_COMPLEX, TEST_CELL, TEST_STRUCTURE,
    TEST_UNSUPPORTED, data_path, temporary_file, temporary_h5file
)
from sdafile.utils import (
    get_decoded, get_record_type, set_encoded, write_header,
)


class TestSDAFileInit(unittest.TestCase):

    def test_mode_r(self):
        self.assertInitNew('r', exc=IOError)
        self.assertInitExisting('r', {}, BadSDAFile)
        self.assertInitExisting('r', BAD_ATTRS, BadSDAFile)
        self.assertInitExisting('r', GOOD_ATTRS)

    def test_mode_r_plus(self):
        self.assertInitNew('r+', exc=IOError)
        self.assertInitExisting('r+', exc=BadSDAFile)
        self.assertInitExisting('r+', exc=BadSDAFile)
        self.assertInitExisting('r+', BAD_ATTRS, BadSDAFile)
        self.assertInitExisting('r+', GOOD_ATTRS)

    def test_mode_w(self):
        self.assertInitNew('w')
        self.assertInitExisting('w')

    def test_mode_x(self):
        self.assertInitNew('x')
        self.assertInitExisting('x', exc=IOError)

    def test_mode_w_minus(self):
        self.assertInitNew('w-')
        self.assertInitExisting('w-', exc=IOError)

    def test_mode_a(self):
        self.assertInitNew('a')
        self.assertInitExisting('a', GOOD_ATTRS)
        self.assertInitExisting('a', BAD_ATTRS, BadSDAFile)
        self.assertInitExisting('a', {}, BadSDAFile)

    def test_mode_default(self):
        with temporary_h5file() as h5file:
            name = h5file.filename
            set_encoded(h5file.attrs, **GOOD_ATTRS)
            h5file.close()
            sda_file = SDAFile(name)
            self.assertEqual(sda_file.mode, 'a')

    def test_pass_kw(self):
        with temporary_file() as file_path:
            sda_file = SDAFile(file_path, 'w', driver='core')
            with sda_file._h5file('r') as h5file:
                self.assertEqual(h5file.driver, 'core')

    def assertAttrs(self, sda_file, attrs={}):
        """ Assert sda_file attributes are equal to passed values.

        if ``attrs`` is empty, check that ``attrs`` take on the default values.

        """
        if attrs == {}:  # treat as if new
            self.assertEqual(sda_file.Created, sda_file.Updated)
            attrs = {}
            write_header(attrs)
            del attrs['Created']
            del attrs['Updated']
            attrs = get_decoded(attrs)

        for attr, expected in attrs.items():
            actual = getattr(sda_file, attr)
            self.assertEqual(actual, expected)

    def assertInitExisting(self, mode, attrs={}, exc=None):
        """ Assert attributes or error when init with existing file.

        Passed ``attrs`` are used when creating the existing file. When ``exc``
        is None, this also tests that the ``attrs`` are preserved.

        """
        with temporary_h5file() as h5file:
            name = h5file.filename
            if attrs is not None and len(attrs) > 0:
                set_encoded(h5file.attrs, **attrs)
            h5file.close()

            if exc is not None:
                with self.assertRaises(exc):
                    SDAFile(name, mode)
            else:
                sda_file = SDAFile(name, mode)
                self.assertAttrs(sda_file, attrs)

    def assertInitNew(self, mode, attrs={}, exc=None):
        """ Assert attributes or error when init with non-existing file. """
        with temporary_file() as file_path:
            os.remove(file_path)
            if exc is not None:
                with self.assertRaises(exc):
                    SDAFile(file_path, mode)
            else:
                sda_file = SDAFile(file_path, mode)
                self.assertAttrs(sda_file)


class TestSDAFileProperties(unittest.TestCase):

    def test_file_properties(self):
        with temporary_file() as file_path:
            sda_file = SDAFile(file_path, 'w')
            self.assertEqual(sda_file.mode, 'w')
            self.assertEqual(sda_file.name, file_path)

    def test_set_writable(self):
        with temporary_file() as file_path:
            sda_file = SDAFile(file_path, 'w')
            self.assertEqual(sda_file.Writable, 'yes')
            sda_file.Writable = 'no'
            self.assertEqual(sda_file.Writable, 'no')

            with self.assertRaises(ValueError):
                sda_file.Writable = True

            with self.assertRaises(ValueError):
                sda_file.Writable = False

            sda_file = SDAFile(file_path, 'r')

            with self.assertRaises(ValueError):
                sda_file.Writable = 'yes'


class TestSDAFileInsert(unittest.TestCase):

    def test_read_only(self):
        with temporary_h5file() as h5file:
            name = h5file.filename
            set_encoded(h5file.attrs, **GOOD_ATTRS)
            h5file.close()
            sda_file = SDAFile(name, 'r')

            with self.assertRaises(IOError):
                sda_file.insert('test', [1, 2, 3])

    def test_no_write(self):
        with temporary_file() as file_path:
            sda_file = SDAFile(file_path, 'w')
            sda_file.Writable = 'no'
            with self.assertRaises(IOError):
                sda_file.insert('test', [1, 2, 3])

    def test_invalid_deflate(self):
        with temporary_file() as file_path:
            sda_file = SDAFile(file_path, 'w')
            with self.assertRaises(ValueError):
                sda_file.insert('test', [1, 2, 3], deflate=-1)

            with self.assertRaises(ValueError):
                sda_file.insert('test', [1, 2, 3], deflate=10)

            with self.assertRaises(ValueError):
                sda_file.insert('test', [1, 2, 3], deflate=None)

    def test_invalid_label(self):
        with temporary_file() as file_path:
            sda_file = SDAFile(file_path, 'w')
            with self.assertRaises(ValueError):
                sda_file.insert('test/', [1, 2, 3])

            with self.assertRaises(ValueError):
                sda_file.insert('test\\', [1, 2, 3])

    def test_label_exists(self):
        with temporary_file() as file_path:
            sda_file = SDAFile(file_path, 'w')
            sda_file.insert('test', [1, 2, 3])
            with self.assertRaises(ValueError):
                sda_file.insert('test', [1, 2, 3])

    def test_timestamp_update(self):
        with temporary_file() as file_path:
            sda_file = SDAFile(file_path, 'w')
            with sda_file._h5file('a') as h5file:
                set_encoded(h5file.attrs, Updated='Unmodified')

            sda_file.insert('test', [0, 1, 2])
            self.assertNotEqual(sda_file.Updated, 'Unmodified')

    def test_invalid_structure_key(self):
        record = [0, 1, 2, {' bad': np.arange(4)}]
        with temporary_file() as file_path:
            sda_file = SDAFile(file_path, 'w')

            with self.assertRaises(ValueError):
                sda_file.insert('something_bad', record)

            self.assertEqual(sda_file.labels(), [])

    def test_insert_called(self):
        with temporary_file() as file_path:
            sda_file = SDAFile(file_path, 'w')
            called = []
            sda_file._registry._inserters = [MockRecordInserter(called)]
            sda_file.insert('foo', True, 'insert_called', 0)

        self.assertEqual(called, ['insert_called'])

    def test_structures(self):
        structure = {
            'foo': 'foo',
            'bar': np.arange(4),
            'baz': np.array([True, False])
        }

        failures = (
            TEST_NUMERIC + TEST_LOGICAL + TEST_CHARACTER + TEST_STRUCTURE +
            TEST_STRUCTURE + TEST_SPARSE + TEST_SPARSE_COMPLEX
        )

        with temporary_file() as file_path:
            sda_file = SDAFile(file_path, 'w')

            # Store homogeneous structures
            label = 'test'
            deflate = 0
            objs = [structure] * 5
            sda_file.insert(label, objs, label, deflate, as_structures=True)
            # Check the type
            with sda_file._h5file('r') as h5file:
                record_type = get_record_type(h5file[label].attrs)
                self.assertEqual(record_type, 'structures')

            # Other record types should fail
            for data in failures:
                with self.assertRaises(ValueError):
                    sda_file.insert('bad', data, 'bad', 0, as_structures=True)

            # Inhomogenous records should fail
            data = [structure, structure.copy()]
            data[0]['baz'] = 10  # change record type
            with self.assertRaises(ValueError):
                sda_file.insert('bad', data, 'bad', 0, as_structures=True)

            del data[0]['baz']
            with self.assertRaises(ValueError):
                sda_file.insert('bad', data, 'bad', 0, as_structures=True)

            # Cell of non-structures should fail
            data = [True]
            with self.assertRaises(ValueError):
                sda_file.insert('bad', data, 'bad', 0, as_structures=True)

    def test_from_file(self):

        with temporary_file() as file_path:
            sda_file = SDAFile(file_path, 'w')
            contents = b'01'

            with temporary_file() as source_file:
                with open(source_file, 'wb') as f:
                    f.write(contents)

                label = sda_file.insert_from_file(source_file)
                sda_file.describe(label, label)
                self.assertTrue(source_file.endswith(label))

    def test_from_file_failure(self):

        with temporary_file() as file_path:
            sda_file = SDAFile(file_path, 'w')

            with temporary_file() as source_file:
                pass

            # The source file is gone
            with self.assertRaises(ValueError):
                sda_file.insert_from_file(source_file)

    def test_unsupported(self):
        with temporary_file() as file_path:
            sda_file = SDAFile(file_path, 'w')
            with sda_file._h5file('a') as h5file:
                set_encoded(h5file.attrs, Updated='Unmodified')

            for i, obj in enumerate(TEST_UNSUPPORTED):
                label = 'test' + str(i)
                with self.assertRaises(ValueError):
                    sda_file.insert(label, obj, label, 0)

            # Make sure the 'Updated' attr does not change
            self.assertEqual(sda_file.Updated, 'Unmodified')


class TestSDAFileExtract(unittest.TestCase):

    def test_invalid_label(self):
        with temporary_file() as file_path:
            sda_file = SDAFile(file_path, 'w')
            with self.assertRaises(ValueError):
                sda_file.extract('test/')

            with self.assertRaises(ValueError):
                sda_file.extract('test\\')

    def test_label_not_exists(self):
        with temporary_file() as file_path:
            sda_file = SDAFile(file_path, 'w')
            with self.assertRaises(ValueError):
                sda_file.extract('test')

    def test_no_timestamp_update(self):
        with temporary_file() as file_path:
            sda_file = SDAFile(file_path, 'w')
            sda_file.insert('test', [0, 1, 2])
            with sda_file._h5file('a') as h5file:
                set_encoded(h5file.attrs, Updated='Unmodified')

            sda_file.extract('test')
            self.assertEqual(sda_file.Updated, 'Unmodified')

    def test_round_trip(self):

        test_set = (
            TEST_NUMERIC + TEST_LOGICAL + TEST_CHARACTER + TEST_STRUCTURE
        )

        def assert_nested_equal(a, b):
            # Unravel lists and tuples
            if isinstance(a, (list, tuple)) or isinstance(b, (list, tuple)):
                assert_equal(len(a), len(b))
                for item_a, item_b in zip(a, b):
                    assert_nested_equal(item_a, item_b)
            else:
                return assert_equal(a, b)

        with temporary_file() as file_path:
            sda_file = SDAFile(file_path, 'w')

            for i, data in enumerate(test_set):
                label = "test" + str(i)
                sda_file.insert(label, data, '', i % 10)
                extracted = sda_file.extract(label)
                assert_equal(extracted, data)

        with temporary_file() as file_path:
            sda_file = SDAFile(file_path, 'w')

            for i, data in enumerate(TEST_CELL):
                label = "test" + str(i)
                sda_file.insert(label, data, '', i % 10)
                extracted = sda_file.extract(label)
                assert_nested_equal(extracted, data)

        test_set = TEST_SPARSE + TEST_SPARSE_COMPLEX

        with temporary_file() as file_path:
            sda_file = SDAFile(file_path, 'w')

            for i, data in enumerate(test_set):
                label = "test" + str(i)
                sda_file.insert(label, data, '', i % 10)
                extracted = sda_file.extract(label)
                expected = data.tocoo()
                self.assertEqual(extracted.dtype, expected.dtype)
                assert_equal(extracted.row, expected.row)
                assert_equal(extracted.col, expected.col)
                assert_equal(extracted.data, expected.data)

    def test_to_file(self):
        with temporary_file() as file_path:
            sda_file = SDAFile(file_path, 'w')
            contents = b'Hello world'
            sda_file.insert('test', io.BytesIO(contents))

            with temporary_file() as destination_path:
                with self.assertRaises(IOError):
                    sda_file.extract_to_file('test', destination_path)

                sda_file.extract_to_file('test', destination_path, True)

                with open(destination_path, 'rb') as f:
                    extracted = f.read()
            self.assertEqual(extracted, contents)

            # The file is closed and gone, try again
            sda_file.extract_to_file('test', destination_path, True)
            with open(destination_path, 'rb') as f:
                extracted = f.read()

            self.assertEqual(extracted, contents)

    def test_to_file_non_file(self):
        with temporary_file() as file_path:
            sda_file = SDAFile(file_path, 'w')
            sda_file.insert('test', 'not a file record')

            with temporary_file() as destination_path:
                with self.assertRaises(ValueError):
                    sda_file.extract_to_file('test', destination_path, True)


class TestSDAFileDescribe(unittest.TestCase):

    def test_read_only(self):
        with temporary_h5file() as h5file:
            name = h5file.filename
            set_encoded(h5file.attrs, **GOOD_ATTRS)
            h5file.close()
            sda_file = SDAFile(name, 'r')

            with self.assertRaises(IOError):
                sda_file.describe('test', 'a test')

    def test_no_write(self):
        with temporary_file() as file_path:
            sda_file = SDAFile(file_path, 'w')
            sda_file.Writable = 'no'
            with self.assertRaises(IOError):
                sda_file.describe('test', 'a test')

    def test_invalid_label(self):
        with temporary_file() as file_path:
            sda_file = SDAFile(file_path, 'w')
            with self.assertRaises(ValueError):
                sda_file.describe('test/', 'a test')

            with self.assertRaises(ValueError):
                sda_file.describe('test\\', 'a test')

    def test_missing_label(self):
        with temporary_file() as file_path:
            sda_file = SDAFile(file_path, 'w')
            with self.assertRaises(ValueError):
                sda_file.describe('test', 'a test')

    def test_happy_path(self):
        with temporary_file() as file_path:
            sda_file = SDAFile(file_path, 'w')
            with sda_file._h5file('a') as h5file:
                set_encoded(h5file.attrs, Updated='Unmodified')

            sda_file.insert('test', [1, 2, 3])
            sda_file.describe('test', 'second')
            with sda_file._h5file('r') as h5file:
                attrs = get_decoded(h5file['test'].attrs, 'Description')
                self.assertEqual(attrs['Description'], 'second')

            # Make sure the 'Updated' attr gets updated
            self.assertNotEqual(sda_file.Updated, 'Unmodified')


class TestSDAFileMisc(unittest.TestCase):

    def test_labels(self):
        with temporary_file() as file_path:
            sda_file = SDAFile(file_path, 'w')
            sda_file.insert('l0', [0])
            sda_file.insert('l1', [1])
            self.assertEqual(sorted(sda_file.labels()), ['l0', 'l1'])

    def test_remove(self):
        with temporary_file() as file_path:
            sda_file = SDAFile(file_path, 'w')

            labels = []
            test_set = (
                TEST_NUMERIC + TEST_LOGICAL + TEST_CHARACTER + TEST_CELL +
                TEST_STRUCTURE + TEST_STRUCTURE + TEST_SPARSE +
                TEST_SPARSE_COMPLEX
            )

            for i, obj in enumerate(test_set):
                label = 'test' + str(i)
                labels.append(label)
                sda_file.insert(label, obj)

            with self.assertRaises(ValueError):
                sda_file.remove()

            with self.assertRaises(ValueError):
                sda_file.remove('not a label')

            random.shuffle(labels)
            removed = labels[::2]
            kept = labels[1::2]

            with sda_file._h5file('a') as h5file:
                set_encoded(h5file.attrs, Updated='Unmodified')

            sda_file.remove(*removed)
            self.assertEqual(sorted(sda_file.labels()), sorted(kept))

            # Make sure metadata is preserved and data can be extracted
            with sda_file._h5file('r') as h5file:
                for label in kept:
                    attrs = h5file[label].attrs
                    self.assertIn('Deflate', attrs)
                    self.assertIn('Description', attrs)
                    self.assertIn('RecordType', attrs)
                    self.assertIn('Empty', attrs)
                    sda_file.extract(label)

            sda_file.remove(*kept)
            self.assertEqual(sda_file.labels(), [])

            self.assertEqual(sda_file.FormatVersion, '1.1')
            self.assertNotEqual(sda_file.Updated, 'Unmodified')

    def test_probe(self):

        cols = [
            'RecordType', 'Description', 'Empty', 'Deflate', 'Complex',
            'ArraySize', 'Sparse', 'RecordSize', 'Class', 'FieldNames',
            'Command',
        ]

        with temporary_file() as file_path:
            sda_file = SDAFile(file_path, 'w')

            labels = []
            for i, obj in enumerate(TEST_NUMERIC[:4]):
                label = 'bar' + str(i)
                labels.append(label)
                sda_file.insert(label, obj, label, i)

            for i, obj in enumerate(TEST_NUMERIC[4:6]):
                label = 'foo' + str(i)
                labels.append(label)
                sda_file.insert(label, obj, label, i)

            state = sda_file.probe()
            state.sort_index()
            self.assertEqual(len(state), 6)
            assert_array_equal(state.columns, cols)
            assert_array_equal(state.index, labels)
            assert_array_equal(state['Description'], labels)
            assert_array_equal(state['Deflate'], [0, 1, 2, 3, 0, 1])

            state = sda_file.probe('bar.*')
            state.sort_index()
            self.assertEqual(len(state), 4)
            assert_array_equal(state.columns, cols)
            assert_array_equal(state.index, labels[:4])
            assert_array_equal(state['Description'], labels[:4])
            assert_array_equal(state['Deflate'], [0, 1, 2, 3])

            state = sda_file.probe('foo.*')
            state.sort_index()
            self.assertEqual(len(state), 2)
            assert_array_equal(state.columns, cols)
            assert_array_equal(state.index, labels[4:])
            assert_array_equal(state['Description'], labels[4:])
            assert_array_equal(state['Deflate'], [0, 1])


class TestSDAFileReplaceUpdate(unittest.TestCase):

    def test_replace(self):
        with temporary_file() as file_path:
            sda_file = SDAFile(file_path, 'w')
            sda_file.insert('test', TEST_NUMERIC[0], 'test_description', 1)

            replacements = TEST_NUMERIC[:1]
            random.shuffle(replacements)
            replacements = replacements[:10]

            with sda_file._h5file('a') as h5file:
                set_encoded(h5file.attrs, Updated='Unmodified')

            for new_data in replacements:
                sda_file.replace('test', new_data)
                assert_equal(sda_file.extract('test'), new_data)
                with sda_file._h5file('r') as h5file:
                    attrs = get_decoded(
                        h5file['test'].attrs, 'Deflate', 'Description'
                    )
                self.assertEqual(attrs['Description'], 'test_description')
                self.assertEqual(attrs['Deflate'], 1)

            self.assertNotEqual(sda_file.Updated, 'Unmodified')

    def test_update_object_on_non_object(self):
        reference_path = data_path('SDAreference.sda')
        with temporary_file() as file_path:
            # Copy the reference, which as an object in it.
            shutil.copy(reference_path, file_path)
            sda_file = SDAFile(file_path, 'a')
            label = 'example A1'
            data = sda_file.extract('example I')
            with self.assertRaises(ValueError):
                sda_file.update_object(label, data)

    def test_update_object_with_equivalent_record(self):

        reference_path = data_path('SDAreference.sda')
        with temporary_file() as file_path:
            # Copy the reference, which as an object in it.
            shutil.copy(reference_path, file_path)
            sda_file = SDAFile(file_path, 'a')
            with sda_file._h5file('a') as h5file:
                set_encoded(h5file.attrs, Updated='Unmodified')

            label = 'example I'

            # Replace some stuff with the same type
            data = sda_file.extract(label)
            data['Parameter'] = np.arange(5)
            sda_file.update_object(label, data)

            extracted = sda_file.extract(label)

            with sda_file._h5file('r') as h5file:
                attrs = get_decoded(h5file['example I'].attrs)

            self.assertNotEqual(sda_file.Updated, 'Unmodified')

        # Validate equality
        self.assertEqual(attrs['RecordType'], 'object')
        self.assertEqual(attrs['Class'], 'ExampleObject')
        self.assertIsInstance(extracted, dict)
        self.assertEqual(len(extracted), 1)
        assert_equal(extracted['Parameter'], data['Parameter'])

    def test_update_object_with_inequivalent_record(self):

        reference_path = data_path('SDAreference.sda')
        with temporary_file() as file_path:
            # Copy the reference, which as an object in it.
            shutil.copy(reference_path, file_path)
            sda_file = SDAFile(file_path, 'a')
            label = 'example I'

            # Replace some stuff with different type
            data = sda_file.extract(label)
            data['Parameter'] = 'hello world'
            with self.assertRaises(ValueError):
                sda_file.update_object(label, data)

    def test_update_object_with_non_record(self):

        reference_path = data_path('SDAreference.sda')
        with temporary_file() as file_path:
            # Copy the reference, which as an object in it.
            shutil.copy(reference_path, file_path)
            sda_file = SDAFile(file_path, 'a')
            label = 'example I'

            # Replace some stuff with a non-dictionary
            with self.assertRaises(ValueError):
                sda_file.update_object(label, 'hello')

    def test_update_objects_on_non_objects(self):
        reference_path = data_path('SDAreference.sda')
        with temporary_file() as file_path:
            # Copy the reference, which as an object in it.
            shutil.copy(reference_path, file_path)
            sda_file = SDAFile(file_path, 'a')
            label = 'example A1'
            data = sda_file.extract('example J')
            with self.assertRaises(ValueError):
                sda_file.update_objects(label, data)

    def test_update_objects_with_equivalent_record(self):

        reference_path = data_path('SDAreference.sda')
        with temporary_file() as file_path:
            # Copy the reference, which as an object in it.
            shutil.copy(reference_path, file_path)
            sda_file = SDAFile(file_path, 'a')
            with sda_file._h5file('a') as h5file:
                set_encoded(h5file.attrs, Updated='Unmodified')

            label = 'example J'

            # Replace some stuff with the same type
            data = sda_file.extract(label)
            data[0, 0]['Parameter'] = np.arange(5)
            sda_file.update_objects(label, data)

            extracted = sda_file.extract(label)

            with sda_file._h5file('r') as h5file:
                attrs = get_decoded(h5file['example J'].attrs)

            self.assertNotEqual(sda_file.Updated, 'Unmodified')

        # Validate equality
        self.assertEqual(attrs['RecordType'], 'objects')
        self.assertEqual(attrs['Class'], 'ExampleObject')
        self.assertIsInstance(extracted, np.ndarray)
        self.assertEqual(extracted.shape, (2, 1))
        assert_equal(extracted[0, 0]['Parameter'], data[0, 0]['Parameter'])
        assert_equal(extracted[1, 0]['Parameter'], data[1, 0]['Parameter'])

    def test_update_objects_with_inequivalent_record(self):

        reference_path = data_path('SDAreference.sda')
        with temporary_file() as file_path:
            # Copy the reference, which as an object in it.
            shutil.copy(reference_path, file_path)
            sda_file = SDAFile(file_path, 'a')
            label = 'example J'

            # Replace some stuff with different type
            data = sda_file.extract(label)
            data[0, 0]['Parameter'] = 'hello world'
            with self.assertRaises(ValueError):
                sda_file.update_objects(label, data)

    def test_update_objects_with_non_record(self):

        reference_path = data_path('SDAreference.sda')
        with temporary_file() as file_path:
            # Copy the reference, which as an object in it.
            shutil.copy(reference_path, file_path)
            sda_file = SDAFile(file_path, 'a')
            label = 'example J'

            # Replace some stuff with a non-dictionary
            with self.assertRaises(ValueError):
                sda_file.update_objects(label, 'hello')
