from nose.tools import *
import pysda.SDAFile as SDAFile


class TestSDAFile:
    def __init__(self):
        self.test_file = SDAFile.SDAFile('refs/SDAreference.sda', mode='r')

    def test_str(self):
        expected = '<SDA file "refs/SDAreference.sda" (mode r)>'
        assert_equal(str(self.test_file), expected)

    def test_repr(self):
        expected = '<SDA file "refs/SDAreference.sda" (mode r)>'
        assert_equal(str(self.test_file), expected)

    def test_formatted_group_output(self):
        expected = 'Label                         Type           Description                                       \n'
        assert_equal(SDAFile._formatted_group_output('Label', 'Type', 'Description'), expected)

    def test_get_attrs(self):
        expected = [u'ReferenceArchive.m', u'example A1', u'example A2',
                    u'example A3', u'example A4', u'example B', u'example C',
                    u'example D', u'example E', u'example F', u'example G',
                    u'example H', u'example I', u'example J']
        assert_equal(self.test_file._get_attrs(), expected)

    def test_format_file_attr(self):
        expected = '       test_key:  \'test_value\'\n'
        assert_equal(SDAFile._format_file_attr('test_key', 'test_value'), expected)

    def test_get_label(self):
        expected = 'file'
        actual = SDAFile.get_record_type('ReferenceArchive.m', self.test_file)
        assert_equal(actual, expected)

    def test_get_description(self):
        expected = '5x1 zeros'
        actual = SDAFile.get_description('example A1', self.test_file)
        assert_equal(actual, expected)
