""" 
Tests the convert_fmproxml_to_json.py module.
"""

import logging, pprint, unittest

from convert_fmproxml_to_json import SourceDictMaker


logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
    datefmt='%d/%b/%Y %H:%M:%S' )
log = logging.getLogger( '__name__' )


class TestConvertXml( unittest.TestCase ):
    """ Tests the convert_fmproxml_to_json.py module. """

    def setUp( self ):
        """ Sets up the test harness. """
        self.maxDiff = None

    def tearDown( self ):
        """ Tears down the test harness. """
        pass

    def test_dictify_data( self ):
        """ Tests the _dictify_data() method. """
        converter = SourceDictMaker()
        test_data = [
            {'Barcode 1': None,
            'Barcode 2': None,
            'Barcode 3': None,
            'Book_Author': None,
            'Book_Date': None,
            'Book_ISBN': None,
            'Book_LC': None,
            'Book_Publisher': None,
            'Box 1 Folder #': None,
            'Box Number': '78B',
            'Box Number 2': None,
            'Box Number 3': 'M-47',
            'Item': 'The Monroe Defense Committee',
            'Notes': None,
            'Number of Folders': None,
            'Organization ID': None,
            'Organization::Name': [None],
            'Organization::Record Type': [None],
            'PartDesignation': None,
            'PartI_BoxNumber': None,
            'PartI_HHNumber_LeadingZeros': None,
            'PartI_MsNumber': None,
            'Record ID': '188135',
            'Type': None},
            {'Barcode 1': None,
            'Barcode 2': None,
            'Barcode 3': None,
            'Book_Author': None,
            'Book_Date': None,
            'Book_ISBN': None,
            'Book_LC': None,
            'Book_Publisher': None,
            'Box 1 Folder #': None,
            'Box Number': '213B',
            'Box Number 2': None,
            'Box Number 3': 'M-39',
            'Item': 'W. Z. Miller',
            'Notes': None,
            'Number of Folders': None,
            'Organization ID': None,
            'Organization::Name': [None],
            'Organization::Record Type': [None],
            'PartDesignation': None,
            'PartI_BoxNumber': None,
            'PartI_HHNumber_LeadingZeros': None,
            'PartI_MsNumber': None,
            'Record ID': '188136',
            'Type': None},
            {'Barcode 1': None,
            'Barcode 2': None,
            'Barcode 3': None,
            'Book_Author': None,
            'Book_Date': None,
            'Book_ISBN': None,
            'Book_LC': None,
            'Book_Publisher': None,
            'Box 1 Folder #': None,
            'Box Number': None,
            'Box Number 2': None,
            'Box Number 3': None,
            'Item': 'feminists lif',
            'Notes': None,
            'Number of Folders': None,
            'Organization ID': 'HH_011507',
            'Organization::Name': ['Minnesota Feminists for Life, Inc.'],
            'Organization::Record Type': ['Organization'],
            'PartDesignation': None,
            'PartI_BoxNumber': None,
            'PartI_HHNumber_LeadingZeros': None,
            'PartI_MsNumber': None,
            'Record ID': '188135',
            'Type': None},
        ]
        expected = {
            '188135': {
                'count': 2,
                'items': [{'Barcode 1': None,
                        'Barcode 2': None,
                        'Barcode 3': None,
                        'Book_Author': None,
                        'Book_Date': None,
                        'Book_ISBN': None,
                        'Book_LC': None,
                        'Book_Publisher': None,
                        'Box 1 Folder #': None,
                        'Box Number': '78B',
                        'Box Number 2': None,
                        'Box Number 3': 'M-47',
                        'Item': 'The Monroe Defense Committee',
                        'Notes': None,
                        'Number of Folders': None,
                        'Organization ID': None,
                        'Organization::Name': [None],
                        'Organization::Record Type': [None],
                        'PartDesignation': None,
                        'PartI_BoxNumber': None,
                        'PartI_HHNumber_LeadingZeros': None,
                        'PartI_MsNumber': None,
                        'Record ID': '188135',
                        'Type': None},
                        {'Barcode 1': None,
                        'Barcode 2': None,
                        'Barcode 3': None,
                        'Book_Author': None,
                        'Book_Date': None,
                        'Book_ISBN': None,
                        'Book_LC': None,
                        'Book_Publisher': None,
                        'Box 1 Folder #': None,
                        'Box Number': None,
                        'Box Number 2': None,
                        'Box Number 3': None,
                        'Item': 'feminists lif',
                        'Notes': None,
                        'Number of Folders': None,
                        'Organization ID': 'HH_011507',
                        'Organization::Name': ['Minnesota Feminists for Life, '
                                                'Inc.'],
                        'Organization::Record Type': ['Organization'],
                        'PartDesignation': None,
                        'PartI_BoxNumber': None,
                        'PartI_HHNumber_LeadingZeros': None,
                        'PartI_MsNumber': None,
                        'Record ID': '188135',
                        'Type': None}]
            },
            '188136': {
                'count': 1,
                'items': [{'Barcode 1': None,
                        'Barcode 2': None,
                        'Barcode 3': None,
                        'Book_Author': None,
                        'Book_Date': None,
                        'Book_ISBN': None,
                        'Book_LC': None,
                        'Book_Publisher': None,
                        'Box 1 Folder #': None,
                        'Box Number': '213B',
                        'Box Number 2': None,
                        'Box Number 3': 'M-39',
                        'Item': 'W. Z. Miller',
                        'Notes': None,
                        'Number of Folders': None,
                        'Organization ID': None,
                        'Organization::Name': [None],
                        'Organization::Record Type': [None],
                        'PartDesignation': None,
                        'PartI_BoxNumber': None,
                        'PartI_HHNumber_LeadingZeros': None,
                        'PartI_MsNumber': None,
                        'Record ID': '188136',
                        'Type': None}]
            }
        }  # end ```expected = {````
        actual = converter._dictify_data( test_data )
        actual = actual['items']
        log.debug( f'actual, ``{pprint.pformat(actual)}``' )
        self.assertEqual( expected, actual )

        # end test_dictify_data()

## end class TestConvertXml()


if __name__ == '__main__':
    unittest.main()
