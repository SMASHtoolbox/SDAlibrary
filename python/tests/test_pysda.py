from nose.tools import *
import pysda


class TestPySDA(object):
    def __init__(self):
        pass

    def test_file_format_check(self):
        with assert_raises(IOError):
            f = pysda.SDAFile('bad_file.sda', mode='r')
