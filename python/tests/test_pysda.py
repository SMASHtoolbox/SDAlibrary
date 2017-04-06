from nose.tools import *
import pysda


def stop_time(f):
    original = time.localtime

    def newf(*args, **kwargs):
        now = original()
        time.localtime = lambda: now
        result = f(*args, **kwargs)
        time.localtime = original
        return result
    return newf


class TestPySDA(object):
    def __init__(self):
        pass

    def test_file_format_check(self):
        with assert_raises(IOError):
            f = pysda.SDAFile('bad_file.sda', mode='r')
