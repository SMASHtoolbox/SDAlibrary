import os

import h5py
from nose.tools import *

import pysda.groups


def setup_module():
    print 'Setting up\n'
    with h5py.File('tests/numericerror.sda', 'w') as err_file:
        gerr = err_file.create_group('err_multi')
        gerr.create_dataset('err_multi', data=[1])
        gerr.create_dataset('d2', data=[1])
        nerr = err_file.create_group('err_badname')
        nerr.create_dataset('asdfasdfasdfasdf', [1])


def test_numeric_record_single_dataset_read():
    with h5py.File('refs/SDAreference.sda', 'r') as f:
        numeric_record_group = pysda.groups.NumericRecord(f['example A1'])
        vals = numeric_record_group.values()
        assert_equal(len(vals), 1)
        assert_equal(type(vals[0]), h5py.Dataset)


@raises(AttributeError)
def test_numeric_record_single_dataset_read_error_multiple():
    with h5py.File('tests/numericerror.sda', 'r') as f:
        numeric_record_group = pysda.groups.NumericRecord(f['err_multi'])


@raises(AttributeError)
def test_numeric_record_single_dataset_read_error_badname():
    with h5py.File('tests/numericerror.sda', 'r') as f:
        numeric_record_group = pysda.groups.NumericRecord(f['err_badname'])


def test_get_local_name():
    with h5py.File('refs/SDAreference.sda', 'r') as f:
        g = pysda.groups.NumericRecord(f['example A1'])
        assert_equal(g.local_name, 'example A1')


def test_numeric_record_single_dataset_create():
    assert False
#
#
# @raises(AttributeError)
# def test_numeric_record_single_dataset_error_on_create_multiple():
#     assert False
#
#
# def test_numeric_record_single_dataset_warn():
#     assert False


def teardown_module():
    print '\n\nTearing down'
    os.remove('tests/numericerror.sda')
