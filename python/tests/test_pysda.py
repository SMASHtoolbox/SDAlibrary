import time

from nose.tools import *
import pysda


def freeze_decorator(time_to_freeze):
    def function_decorator(func):
        original = time.localtime

        def newf(*args, **kwargs):
            time.localtime = lambda: time_to_freeze
            result = f(*args, **kwargs)
            time.localtime = original
            return result
        return newf
    return function_decorator


class TestPySDA(object):
    test_time = 1483254000  # January 1st, 2017 00:00:00

    def __init__(self):
        pass

    @freeze_decorator(test_time)
    def test_created_time(self):
        f = pysda.SDAFile('test.sda', 'w')
        expected = time.localtime(TestPySDA.test_time)
        actual = f.attrs['Created']
        assert_equal(actual, expected)
