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

    def __init__(self):
        pass

    @freeze_decorator(test_time)
    def test_created_time(self):
        f = pysda.SDAFile('test.sda', 'w')
        expected = "01-Jan-2017 00:00:00"
        actual = f.attrs['Created']
        assert_equal(actual, expected)

    def test_format_time(self):
        expected = "01-Jan-2017 00:00:00"
        actual = pysda._format_time(TestPySDA.test_time)
        assert_equal(actual, expected)
