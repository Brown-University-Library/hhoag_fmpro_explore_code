import argparse, logging, os, pathlib
# import xml.etree.ElementTree as ET
from xml.dom import minidom

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


def pretty_print_xml( input_filepath: str, output_filepath: str ):
    """ Just outputs a pretty-printed XML file.
        Called by dundermain. """
    ## load file
    with open( input_filepath, 'r' ) as f:
        xml_string = f.read()
    ## format the xml    
    dom = minidom.parseString( xml_string )
    formatted_xml = dom.toprettyxml()
    ## write output file
    with open( output_filepath, 'w' ) as f:
        f.write( formatted_xml )
    return


# def pretty_print_xml( input_filepath: str, output_filepath: str ):
#     """ Just outputs a pretty-printed XML file.
#         Called by dundermain. """
#     # Parse the XML file
#     tree = ET.parse(input_filepath)
#     root = tree.getroot()

#     # Create a string with pretty-printed XML
#     pretty_xml = ET.tostring(root, encoding='unicode', method='xml')
    
#     # Add indentation
#     from xml.dom import minidom
#     dom = minidom.parseString(pretty_xml)
#     pretty_xml_as_string = dom.toprettyxml()

#     # Write the pretty-printed XML to a new file
#     with open(output_filepath, 'w') as f:
#         f.write(pretty_xml_as_string)


def make_output_path( input_path: str ):
    """ Makes an output path from the input path.
        Called by dundermain. """
    input_path_obj = pathlib.Path(input_path)
    dir_path = input_path_obj.parent
    filename_without_ext = input_path_obj.stem
    file_extension = input_path_obj.suffix
    output_path = f'{dir_path}/{filename_without_ext}_formatted{file_extension}'
    log.debug( f'output_path: {output_path}' )
    return output_path


if __name__ == '__main__':
    ## set up argparser
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--input_path', type=str, help='Path to the input file')
    args = parser.parse_args()
    log.debug( f'args: {args}' )
    ## get input path
    input_path = args.input_path if args.input_path else "../source_xml_files/2023-11-10_items_xml_export.xml"
    log.debug( f'input_path: {input_path}' )
    ## make output path
    output_path: str = make_output_path( input_path )
    ## get to work
    pretty_print_xml( input_path, output_path )
    log.debug( 'done' )