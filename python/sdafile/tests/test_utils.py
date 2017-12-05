import datetime
from itertools import combinations
import unittest

import numpy as np
from numpy.testing import assert_array_equal

from sdafile.exceptions import BadSDAFile
from sdafile.record_inserter import InserterRegistry
from sdafile.testing import (
    BAD_ATTRS, GOOD_ATTRS, temporary_h5file
)
from sdafile.utils import (
    CELL_EQUIVALENT, STRUCTURE_EQUIVALENT, SUPPORTED_RECORD_TYPES,
    are_record_types_equivalent, are_signatures_equivalent, error_if_bad_attr,
    error_if_bad_header, error_if_not_writable, get_date_str, get_decoded,
    get_empty_for_type, is_valid_date, is_valid_file_format,
    is_valid_format_version, is_valid_matlab_field_label, is_valid_writable,
    set_encoded, unnest, unnest_record, update_header, write_header
)


class TestUtils(unittest.TestCase):

    def test_are_record_types_equivalent(self):

        for rt in SUPPORTED_RECORD_TYPES:
            self.assertTrue(are_record_types_equivalent(rt, rt))

        equivalents = []
        for rt1, rt2 in combinations(SUPPORTED_RECORD_TYPES, 2):
            if are_record_types_equivalent(rt1, rt2):
                equivalents.append(sorted((rt1, rt2)))

        expected = []
        for rt1, rt2 in combinations(STRUCTURE_EQUIVALENT, 2):
            expected.append(sorted((rt1, rt2)))

        for rt1, rt2 in combinations(CELL_EQUIVALENT, 2):
            expected.append(sorted((rt1, rt2)))

        self.assertEqual(sorted(equivalents), sorted(expected))

    def test_are_signatures_equivalent(self):

        sig = (
            ('', 'structure'),
            ('a', 'numeric'),
            ('b', 'logical'),
            ('c', 'character')
        )
        self.assertTrue(are_signatures_equivalent(sig, sig))
        self.assertFalse(are_signatures_equivalent(sig, sig[1:]))
        self.assertFalse(are_signatures_equivalent(sig, sig[::-1]))

        sig2 = (
            ('', 'structure'),
            ('a', 'numeric'),
            ('b', 'logical'),
            ('d', 'character')
        )
        self.assertFalse(are_signatures_equivalent(sig, sig2))

        sig3 = (
            ('', 'structure'),
            ('a', 'numeric'),
            ('b', 'logical'),
            ('c', 'numeric')
        )
        self.assertFalse(are_signatures_equivalent(sig, sig3))

    def test_unnest(self):
        data = dict(a=1, b=True, c='foo')
        registry = InserterRegistry()
        answer = unnest(data, registry)
        expected = (
            ('', 'structure'),
            ('a', 'numeric'),
            ('b', 'logical'),
            ('c', 'character')
        )
        self.assertEqual(answer, expected)

        self.assertEqual(unnest(1, registry), (('', 'numeric'),))
        self.assertEqual(unnest(True, registry), (('', 'logical'),))
        self.assertEqual(unnest('foo', registry), (('', 'character'),))
        self.assertEqual(unnest([], registry), (('', 'cell'),))
        self.assertEqual(unnest({}, registry), (('', 'structure'),))

        data = dict(
            a=1, b=True, c=dict(d='foo', e=5, f=dict(g=6)),
            h=['hello', np.arange(5)],
        )
        answer = unnest(data, registry)
        expected = (
            ('', 'structure'),
            ('a', 'numeric'),
            ('b', 'logical'),
            ('c', 'structure'),
            ('h', 'cell'),
            ('c/d', 'character'),
            ('c/e', 'numeric'),
            ('c/f', 'structure'),
            ('h/element 1', 'character'),
            ('h/element 2', 'numeric'),
            ('c/f/g', 'numeric'),
        )
        self.assertEqual(answer, expected)

    def test_unnest_record(self):
        with temporary_h5file() as h5file:
            grp = h5file.create_group('test')
            set_encoded(grp.attrs, RecordType='structure')
            sub_grp = grp.create_group('a')
            set_encoded(sub_grp.attrs, RecordType='numeric')
            sub_grp = grp.create_group('b')
            set_encoded(sub_grp.attrs, RecordType='logical')
            sub_grp = grp.create_group('c')
            set_encoded(sub_grp.attrs, RecordType='cell')
            sub_sub_grp = sub_grp.create_group('e')
            set_encoded(sub_sub_grp.attrs, RecordType='numeric')
            sub_sub_grp = sub_grp.create_group('f')
            set_encoded(sub_sub_grp.attrs, RecordType='numeric')
            sub_grp = grp.create_group('d')
            set_encoded(sub_grp.attrs, RecordType='character')

            answer = unnest_record(grp)
            expected = (
                ('', 'structure'),
                ('a', 'numeric'),
                ('b', 'logical'),
                ('c', 'cell'),
                ('d', 'character'),
                ('c/e', 'numeric'),
                ('c/f', 'numeric'),
            )
            self.assertEqual(answer, expected)

    def test_error_if_bad_attr(self):
        with temporary_h5file() as h5file:

            # No attr -> bad
            with self.assertRaises(BadSDAFile):
                error_if_bad_attr(h5file, 'foo', lambda value: value == 'foo')

            # Wrong attr -> bad
            h5file.attrs['foo'] = b'bar'
            with self.assertRaises(BadSDAFile):
                error_if_bad_attr(h5file, 'foo', lambda value: value == 'foo')

            # Right attr -> good
            h5file.attrs['foo'] = b'foo'
            error_if_bad_attr(h5file, 'foo', lambda value: value == 'foo')

    def test_error_if_bad_header(self):
        with temporary_h5file() as h5file:

            attrs = h5file.attrs

            # Write a good header
            for attr, value in GOOD_ATTRS.items():
                attrs[attr] = value.encode('ascii')
            error_if_not_writable(h5file)

            # Check each bad value
            for attr, value in BAD_ATTRS.items():
                attrs[attr] = value.encode('ascii')

                with self.assertRaises(BadSDAFile):
                    error_if_bad_header(h5file)

    def test_error_if_not_writable(self):
        with temporary_h5file() as h5file:
            h5file.attrs['Writable'] = b'yes'
            error_if_not_writable(h5file)

            h5file.attrs['Writable'] = b'no'
            with self.assertRaises(IOError):
                error_if_not_writable(h5file)

    def test_get_date_str(self):
        dt = datetime.datetime(2017, 8, 18, 2, 22, 11)
        date_str = get_date_str(dt)
        self.assertEqual(date_str, '18-Aug-2017 02:22:11')

        dt = datetime.datetime(2017, 8, 18, 1, 1, 1)
        date_str = get_date_str(dt)
        self.assertEqual(date_str, '18-Aug-2017 01:01:01')

        dt = datetime.datetime(2017, 8, 18, 0, 0, 0)
        date_str = get_date_str(dt)
        self.assertEqual(date_str, '18-Aug-2017')

        date_str = get_date_str()  # valid without arguments

    def test_get_empty_for_type(self):
        self.assertEqual('', get_empty_for_type('character'))
        assert_array_equal(
            np.array([], dtype=bool), get_empty_for_type('logical')
        )
        self.assertEqual(get_empty_for_type('file'), b'')
        self.assertTrue(np.isnan(get_empty_for_type('numeric')))
        self.assertEqual(get_empty_for_type('cell'), [])
        self.assertEqual(get_empty_for_type('structure'), {})

    def test_is_valid_date(self):
        self.assertTrue(is_valid_date('18-Aug-2017 02:22:11'))
        self.assertTrue(is_valid_date('18-Aug-2017'))
        self.assertFalse(is_valid_date('2017-01-01 01:23:45'))

    def test_is_valid_file_format(self):
        self.assertTrue(is_valid_file_format('SDA'))
        self.assertFalse(is_valid_file_format('sda'))
        self.assertFalse(is_valid_file_format('SDB'))

    def test_is_valid_format_version(self):
        self.assertTrue(is_valid_format_version('1.0'))
        self.assertTrue(is_valid_format_version('1.1'))
        self.assertFalse(is_valid_format_version('1.2'))
        self.assertFalse(is_valid_format_version('0.2'))
        self.assertFalse(is_valid_format_version('2.0'))

    def test_is_valid_matlab_field_label(self):
        self.assertTrue(is_valid_matlab_field_label('a0n1'))
        self.assertTrue(is_valid_matlab_field_label('a0n1999999'))
        self.assertTrue(is_valid_matlab_field_label('a0_n1'))
        self.assertTrue(is_valid_matlab_field_label('a0_N1'))
        self.assertTrue(is_valid_matlab_field_label('A0_N1'))
        self.assertFalse(is_valid_matlab_field_label(''))
        self.assertFalse(is_valid_matlab_field_label(' '))
        self.assertFalse(is_valid_matlab_field_label('1n0a'))
        self.assertFalse(is_valid_matlab_field_label('A0 N1'))
        self.assertFalse(is_valid_matlab_field_label('_A0N1'))
        self.assertFalse(is_valid_matlab_field_label(' a0n1'))
        self.assertFalse(is_valid_matlab_field_label(' A0N1'))

    def test_is_valid_writable(self):
        self.assertTrue(is_valid_writable('yes'))
        self.assertTrue(is_valid_writable('no'))
        self.assertFalse(is_valid_writable('YES'))
        self.assertFalse(is_valid_writable('NO'))
        self.assertFalse(is_valid_writable(True))
        self.assertFalse(is_valid_writable(False))

    def test_get_decoded(self):
        attrs = {'a': b'foo', 'b': b'bar', 'c': 9}
        decoded = get_decoded(attrs, 'a', 'c', 'd')
        self.assertEqual(sorted(decoded.keys()), ['a', 'c'])
        self.assertEqual(decoded['a'], 'foo')
        self.assertEqual(decoded['c'], 9)

        # Get everything
        decoded = get_decoded(attrs)
        self.assertEqual(sorted(decoded.keys()), ['a', 'b', 'c'])
        self.assertEqual(decoded['a'], 'foo')
        self.assertEqual(decoded['b'], 'bar')
        self.assertEqual(decoded['c'], 9)

    def test_set_encoded(self):
        encoded = {}
        set_encoded(encoded, a='foo', b='bar', c=9)
        self.assertEqual(sorted(encoded.keys()), ['a', 'b', 'c'])
        self.assertEqual(encoded['a'], b'foo')
        self.assertEqual(encoded['b'], b'bar')
        self.assertEqual(encoded['c'], 9)

    def test_update_header(self):
        attrs = {}
        update_header(attrs)
        self.assertEqual(len(attrs), 2)
        self.assertEqual(attrs['FormatVersion'], b'1.1')
        self.assertIsNotNone(attrs['Updated'])

    def test_write_header(self):
        attrs = {}
        write_header(attrs)
        self.assertEqual(len(attrs), 5)
        self.assertEqual(attrs['FileFormat'], b'SDA')
        self.assertEqual(attrs['FormatVersion'], b'1.1')
        self.assertEqual(attrs['Writable'], b'yes')
        self.assertEqual(attrs['Created'], attrs['Updated'])
        self.assertIsNotNone(attrs['Updated'])
