"""
Outputs unique organization-IDs, with counts.
Note: the count appears to be 'boxes' not 'items'.

Usage:
    python unique_collections.py --input_path "/path/to/file.xml"

Output:
(as of 2023-Nov-16)
    len(row_elements), ``177237``
    len(unique_organization_ids), ``39137``
    orgs sorted by count: [
        ('HH_035484', 5258),
        ('HH_035483', 3751),
        ('HH_022330', 1594),
        ('HH_035485', 843),
        etc...

Notes:
- over 23K organizations have only 1 item.
- if the number of row-elements (items) is c.177K, and our number of scans is c.800K, then there are an _average_ of c.4.5 pages per item.
"""

import argparse, logging, os, pprint
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

    ## instantiate holders
    unique_organization_ids = set()
    items_per_organization = {}

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
            org_id = data_element.text.strip()
            unique_organization_ids.add(org_id)
            ## increment org count
            items_per_organization[org_id] = items_per_organization.get(org_id, 0) + 1

    ## output results
    log.info( f'len(unique_organization_ids), ``{len(unique_organization_ids)}``' )
    orgs_sorted_by_count = sorted(items_per_organization.items(), key=lambda x: x[1], reverse=True)
    log.info( f'orgs sorted by count: {pprint.pformat(orgs_sorted_by_count)}' )

    return


if __name__ == '__main__':
    ## set up argparser
    parser = argparse.ArgumentParser(description='Outputs unique organization-IDs, with counts')
    parser.add_argument('--input_path', type=str, help='Path to the input file')
    args = parser.parse_args()
    log.debug( f'args: {args}' )
    ## get input path
    input_path = args.input_path if args.input_path else "../source_xml_files/2023-11-10_items_xml_export_formatted.xml"
    log.debug( f'input_path: {input_path}' )
    ## get to work
    get_collection_info( input_path )
    log.debug( 'done' )