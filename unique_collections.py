"""
Outputs number of unique organization-IDs.

Usage:
    python unique_collections.py --input_path "/path/to/file.xml"

Output:
(as of 2023-Nov-16)
    len(row_elements), ``177237``
    len(unique_organization_ids), ``39137``

Note that if the number of row-elements (items) is c.177K, and our number of scans is c.800K, then there are an _average_ of c.4.5 pages per item.
"""

import argparse, logging, os
import xml.etree.ElementTree as ET

lglvl: str = os.environ.get( 'LOGLEVEL', 'DEBUG' )
lglvldct = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO }
logging.basicConfig(
    level=lglvldct[lglvl],  # assigns the level-object to the level-key
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
    datefmt='%d/%b/%Y %H:%M:%S' )
log = logging.getLogger( __name__ )
log.debug( 'logging working' )


def get_collection_info( source_filepath: str ) -> None:

    ## load file
    with open( source_filepath, 'r' ) as f:
        source_xml_string: str = f.read()

    ## define and register namespace ( needed for find() and findall() )
    ns = {'fmp': 'http://www.filemaker.com/fmpxmlresult'}
    ET.register_namespace('', ns['fmp'])  # can be done before or after making the xml-object

    ## instantiate xml object
    xml_obj: ET.Element = ET.fromstring( source_xml_string )

    ## instantiate set for unique-ids   
    unique_organization_ids = set()

    ## get all row elements
    row_elements: list = xml_obj.findall('.//fmp:ROW', ns)
    log.info( f'len(row_elements), ``{len(row_elements)}``' )
    assert type( row_elements[0] ) == ET.Element

    ## iterate through each ROW element
    for row_element in row_elements:
        ## Get first COL/DATA element (the org-id)
        data_element = row_element.find('.//fmp:COL/fmp:DATA', ns)  # type(data_element) == ET.Element
        # log.debug( f'data_element: ``{data_element}``')
        if data_element is not None and data_element.text is not None:
            unique_organization_ids.add(data_element.text.strip())

    ## output results
    log.info( f'len(unique_organization_ids), ``{len(unique_organization_ids)}``' )
    # log.debug( f'unique_organization_ids, ``{unique_organization_ids}``' )

    return


if __name__ == '__main__':
    ## set up argparser
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--input_path', type=str, help='Path to the input file')
    args = parser.parse_args()
    log.debug( f'args: {args}' )
    ## get input path
    input_path = args.input_path if args.input_path else "../source_xml_files/2023-11-10_items_xml_export_formatted.xml"
    log.debug( f'input_path: {input_path}' )
    ## get to work
    get_collection_info( input_path )
    log.debug( 'done' )