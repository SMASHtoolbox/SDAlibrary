import functools
import time

from nose.tools import *
import pysda


def freeze_decorator(time_to_freeze):
    def function_decorator(func):
        original = time.localtime

        @functools.wraps(func)
        def newf(*args, **kwargs):
            time.localtime = lambda __: time_to_freeze
            result = func(*args, **kwargs)
            time.localtime = original
            return result
        return newf
    return function_decorator


class TestPySDA(object):
    test_time = time.localtime(1483254000)  # January 1st, 2017 00:00:00
    test_update_time = time.localtime(1483254001)

    def __init__(self):
        pass

    @freeze_decorator(test_time)
    def test_init(self):
        f = pysda.SDAFile('test.sda', 'w')
        assert_equal(f.attrs['FileFormat'], 'SDA')
        assert_equal(f.attrs['FormatVersion'], '1.1')
        assert_equal(f.attrs['Writable'], 'yes')
        assert_equal(f.attrs['Created'], "01-Jan-2017 00:00:00")
        assert_equal(f.attrs['Updated'], "01-Jan-2017 00:00:00")
