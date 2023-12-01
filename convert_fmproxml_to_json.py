import argparse, datetime, json, logging, os, pprint, random
import lxml
from lxml import etree


logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
    datefmt='%d/%b/%Y %H:%M:%S' )
log = logging.getLogger( '__name__' )


class SourceDictMaker:
    """ Handles creation of an accession_number-to-item-info dict, saved as a json file.
        Purpose: This is one of the essential files that should exist before doing almost any bell processing.
                 It converts the raw filemaker-pro xml into json data for easy processing and viewing.
        if __name__... at bottom indicates how to run this script. """

    def __init__( self ):
        self.NAMESPACE = { 'default': 'http://www.filemaker.com/fmpxmlresult' }
        self.expected_column_count = 24  # as of 2023-11-10 export

    def convert_fmproxml_to_json(
        self, FMPRO_XML_PATH, JSON_OUTPUT_PATH ):
        """ CONTROLLER
            Produces accession-number dict, and saves to a json file.
            Example: { count:5000,
                   #   datetime: 2013...,
                   #   items:{ accnum_1:{artist:abc, title:def}, accnum_2:{etc.}, etc. }
                   # } """
        #Get data
        #Purpose: gets raw filemaker-pro xml unicode-string from gist
        log.info( 'getting data' )
        unicode_xml_string = self._get_data( FMPRO_XML_PATH )
        #
        #Docify xml string
        #Purpose: converts unicode-string to <type 'lxml.etree._Element'>
        log.info( 'docifying xml' )
        XML_DOC = self._docify_xml( unicode_xml_string)
        #
        #Make key list
        #Purpose: creates list of keys that will be used for each item-dict
        #Example returned data: [ 'object_id', 'object_title', 'object_date', etc. ]
        log.info( 'making dict-keys' )
        dict_keys = self._make_dict_keys( XML_DOC, self.NAMESPACE )
        #
        #Make list of doc-items
        #Purpose: creates list of xml-doc items
        log.info( 'making xml-doc rows' )
        xml_doc_rows = self._get_xml_doc_rows( XML_DOC, self.NAMESPACE )
        #
        #Make initial dict-list
        #Purpose: creates initial list of dict-items. For a given key, the value-type may vary by item.
        #Example returned data: [ {'artist_alias': 'abc', 'artist_birth_country_id': '123', etc.}, {etc.}, ... ]
        log.info( 'making initial dict-list' )
        result_list = self._process_rows( xml_doc_rows, self.NAMESPACE, dict_keys )
        #
        #Make key-type dict
        #Purpose: creats dict of key-name:key-type; all data examined to see which keys should have list vs unicode-string values.
        #Example returned data: [  {'ARTISTS::calc_nationality': <type 'list'>, 'ARTISTS::use_alias_flag': <type 'unicode'>, etc.} ]
        log.info( 'making key-type dict' )
        key_type_dict = self._make_key_type_dict( result_list )
        #
        #Normalize dict-values
        #Purpose: creates final list of dict-items. For a given key, the value-type will _not_ vary by item.
        #Example returned data: [ {'artist_alias': ['abc'], 'artist_birth_country_id': ['123'], etc.}, {etc.}, ... ]
        log.info( 'normalizing dict-values' )
        result_list = self._normalize_value_types( key_type_dict, result_list )
        #
        #Dictify item-list
        #Purpose: creates accession-number to item-data-dict dictionary, adds count & datestamp
        #Example returned data: { count:5000,
                              #   items:{ accnum_1:{artist:abc, title:def}, accnum_2:{etc.}, etc. }
                              # }
        log.info( 'dictifying data' )
        dictified_data = self._dictify_data( result_list )
        #
        #Output json
        log.info( 'saving json' )
        self._save_json( dictified_data, JSON_OUTPUT_PATH )

    def _get_data( self, FMPRO_XML_PATH ):
        """ Reads and returns source filemaker pro xml. """
        with open( FMPRO_XML_PATH, 'rt' ) as f:
          unicode_data = f.read()
        assert type(unicode_data) == str
        return unicode_data

    def _docify_xml( self, unicode_xml_string):
        ''' Returns xml-doc. '''
        byte_string = unicode_xml_string.encode('utf-8', 'replace')
        parser = etree.XMLParser()
        XML_DOC = etree.fromstring( byte_string, parser )  # str required because xml contains an encoding declaration
        assert type(XML_DOC) == lxml.etree._Element, type(XML_DOC)  # type: ignore
        return XML_DOC

    def _make_dict_keys( self, XML_DOC, NAMESPACE ):
        ''' Returns list of field names; they'll later become keys in each item-dict. '''
        assert type(XML_DOC) == lxml.etree._Element, type(XML_DOC)
        xpath = '/default:FMPXMLRESULT/default:METADATA/default:FIELD'
        elements = XML_DOC.xpath( xpath, namespaces=(NAMESPACE) )
        dict_keys = []
        for e in elements:
          dict_keys.append( e.attrib['NAME'] )
        assert type(dict_keys) == list, type(dict_keys)
        return dict_keys

    def _get_xml_doc_rows( self, XML_DOC, NAMESPACE ):
        ''' Returns list of item docs. '''
        assert type(XML_DOC) == lxml.etree._Element, type(XML_DOC)
        xpath = '/default:FMPXMLRESULT/default:RESULTSET/default:ROW'
        rows = XML_DOC.xpath( xpath, namespaces=(NAMESPACE) )
        assert type(rows) == list, type(rows)
        sample_element = rows[0]
        assert type(sample_element) == lxml.etree._Element, type(sample_element)
        return rows

    def _process_rows( self, xml_doc_rows, NAMESPACE, dict_keys ):
        ''' Returns list of item dictionaries.
            Calls _make_data_dict() helper. '''
        result_list = []
        for i,row in enumerate(xml_doc_rows):
          ## get columns (fixed number of columns per row)
          xpath = 'default:COL'
          columns = row.xpath( xpath, namespaces=(NAMESPACE) )
          assert len(columns) == self.expected_column_count, len(columns)
          ## get data_elements (variable number per column)
          item_dict = self._makeDataDict( columns, NAMESPACE, dict_keys )
          result_list.append( item_dict )  # if i > 5: break
        return result_list

    def _makeDataDict( self, columns, NAMESPACE, keys ):
        ''' Returns info-dict for a single item; eg { 'artist_first_name': 'andy', 'artist_last_name': 'warhol' }
            Called by: _process_rows()
            Calls: self.__run_asserts(), self.__handle_single_element(), self.__handle_multiple_elements() '''
        self.__run_asserts( columns, keys )
        xpath = 'default:DATA'; d_dict = {}  # setup
        for i,column in enumerate(columns):
            data = column.xpath( xpath, namespaces=(NAMESPACE) )  # type(data) always a list, but of an empty, a single or multiple elements?
            if len(data) == 0:    # eg <COL(for artist-firstname)></COL>
                d_dict[ keys[i] ] = None
            elif len(data) == 1:  # eg <COL(for artist-firstname)><DATA>'artist_firstname'</DATA></COL>
                d_dict[ keys[i] ] = self.__handle_single_element( data, keys[i] )
            else:                 # eg <COL(for artist-firstname)><DATA>'artist_a_firstname'</DATA><DATA>'artist_b_firstname'</DATA></COL>
                d_dict[ keys[i] ] = self.__handle_multiple_elements( data, keys[i] )
        return d_dict

    def __run_asserts( self, columns, keys ):
        ''' Documents the inputs.
            Called by _makeDataDict() '''
        assert type(columns) == list, type(columns)
        assert type(columns[0]) == lxml.etree._Element, type(columns[0])
        assert type(keys) == list, type(keys)
        return

    def __handle_single_element( self, data, the_key ):
        ''' Stores either None or the single unicode value to the key.
            Called by _makeDataDict() '''
        return_val = None
        if data[0].text:
            if type( data[0].text ) == str:
                return_val = data[0].text.strip()
            else:
                return_val = data[0].text.decode( 'utf-8', 'replace' ).strip()
        return return_val

    def __handle_multiple_elements( self, data, the_key ):
        ''' Stores list of unicode values to the key.
            Called by _makeDataDict() '''
        d_list = []
        for data_element in data:
            if data_element.text:
                if type( data_element.text ) == str:
                    d_list.append( data_element.text.strip() )
                else:
                    d_list.append( data_element.text.decode('utf-8', 'replace').strip() )
            else:
                d_list.append( None )
        return d_list

    def _make_key_type_dict( self, result_list ):
        ''' Determines whether value of given key should be a unicode-string or a list.
            Called by convert_fmproxml_to_json()
            TODO: look into this more. '''
        key_type_dict = {}
        for entry_dict in result_list:
          for (key,value) in entry_dict.items():
            if not key in key_type_dict.keys():
              key_type_dict[key] = str
            if type(value) == list and len(value) > 0:
              key_type_dict[key] = list
        return key_type_dict

    def _normalize_value_types( self, key_type_dict, result_list ):
        ''' Determines stable type for each field. '''
        updated_result_list = []
        assert len( key_type_dict.keys() ) == self.expected_column_count
        for entry_dict in result_list:
          assert len( entry_dict.keys() ) == self.expected_column_count
          for key, val in entry_dict.items():
            if key_type_dict[key] == list and ( type(val) == str or val == None ) :
              entry_dict[key] = [ val ]
          updated_result_list.append( entry_dict )
        return updated_result_list

    def _dictify_data( self, source_list ):
        """ Takes raw bell list of dict_data, returns accession-number dict. """
        rec_num_dict = {}
        num_duplicates = 0
        for i, entry in enumerate( source_list ):
            if i % 1000 == 0:
                log.debug(f'i, `{i}`')
            if entry['Record ID']:  # handles a null entry
                rec_num = entry['Record ID'].strip()
                if rec_num in rec_num_dict:
                    #print out the error, with the information about what's duplicated
                    #don't raise an exception, because we want to find all the duplicates in one run
                    print(f'duplicate accession number: "{rec_num}"')
                    # print(f'  object_id: {entry["object_id"]}; title: {entry["object_title"]}')
                    # print(f'  object_id: {rec_num_dict[rec_num]["object_id"]}; title: {rec_num_dict[rec_num]["object_title"]}')
                    num_duplicates += 1
                    random_num = random.randint(1000, 9999)
                    temp_rec_num = f'{rec_num}_{random_num}'
                else:
                    rec_num_dict[rec_num] = entry
            else:
                log.info( f'no rec_num for entry, ``{}``' )
                # print(f'  object_id: {entry["object_id"]}; title: {entry["object_title"]}')
        final_dict = {
          'count': len( rec_num_dict.items() ),
          'datetime': str( datetime.datetime.now() ),
          'items': rec_num_dict }
        print(f'Total records in DB: {len(source_list)}')
        print(f'Valid items: {final_dict["count"]}')
        print(f'number of duplicates: {num_duplicates}')
        return final_dict

    # def _dictify_data( self, source_list ):
    #     """ Takes raw bell list of dict_data, returns accession-number dict. """
    #     accession_number_dict = {}
    #     num_duplicates = 0
    #     for entry in source_list:
    #         if entry['calc_accession_id']:  # handles a null entry
    #             accession_num = entry['calc_accession_id'].strip()
    #             if accession_num in accession_number_dict:
    #                 #print out the error, with the information about what's duplicated
    #                 #don't raise an exception, because we want to find all the duplicates in one run
    #                 print(f'duplicate accession number: "{accession_num}"')
    #                 print(f'  object_id: {entry["object_id"]}; title: {entry["object_title"]}')
    #                 print(f'  object_id: {accession_number_dict[accession_num]["object_id"]}; title: {accession_number_dict[accession_num]["object_title"]}')
    #                 num_duplicates += 1
    #             accession_number_dict[accession_num] = entry
    #         else:
    #             print(f'no accession number for record')
    #             print(f'  object_id: {entry["object_id"]}; title: {entry["object_title"]}')
    #     final_dict = {
    #       'count': len( accession_number_dict.items() ),
    #       'datetime': str( datetime.datetime.now() ),
    #       'items': accession_number_dict }
    #     print(f'Total records in DB: {len(source_list)}')
    #     print(f'Valid items: {final_dict["count"]}')
    #     print(f'number of duplicates: {num_duplicates}')
    #     return final_dict

    def _save_json( self, result_list, JSON_OUTPUT_PATH ):
        ''' Saves the list of item-dicts to .json file. '''
        json_string = json.dumps( result_list, indent=2, sort_keys=True )
        with open( JSON_OUTPUT_PATH, 'wt' ) as f:
            f.write( json_string )
        return

  # end class SourceDictMaker()
    

if __name__ == '__main__':
    log.info( 'starting dundermain' )
    start_time = datetime.datetime.now()
    ## get args -----------------------------------------------------
    parser = argparse.ArgumentParser( description='expects source-xml-path, and output-json-path.' )
    parser.add_argument( '--source_path', type=str, help='path to source xml file' )
    parser.add_argument( '--output_path', type=str, help='path to output json file' )
    args = parser.parse_args()
    FMPRO_XML_PATH = args.source_path
    JSON_OUTPUT_PATH = args.output_path
    ## run converter ------------------------------------------------
    maker = SourceDictMaker()
    maker.convert_fmproxml_to_json( FMPRO_XML_PATH, JSON_OUTPUT_PATH )
    elapsed_time = datetime.datetime.now() - start_time
    log.info( 'ending dundermain; elapsed_time, ``%s``' % elapsed_time )
