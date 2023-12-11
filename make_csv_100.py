"""
Makes a TSV file from a FileMaker Pro jsonized export.

Notes:
- Only includes rows where the `Organization ID` value is in the STARTING_ORGS list.
- the output file will not overwrite previous output files -- because a timestamp is included in the filename.
- TODO: the output file is hard-coded to go to a '../created_tsv_files/' dir; add an output-path argument.

Usage:
(venv) $ python ./make_csv_100.py --input_path "/path/to/file.json"
"""

import argparse, csv, datetime, json, logging, os, pprint


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


## manager function -------------------------------------------------
def make_csv_from_fmpro_json( input_path: str ) -> None:
    ## make target orgs-list ----------------------------------------
    # target_orgs: list = STARTING_ORGS.split()
    target_orgs: list = make_starting_orgs_list()
    sorted_target_orgs: list = sorted( target_orgs )
    ## load json file -----------------------------------------------
    with open( input_path, 'r' ) as f:
        source_json_string: str = f.read()
    ## load up python dict ------------------------------------------
    data_dct = json.loads( source_json_string )
    rows_dct: dict = data_dct['items']
    assert type(rows_dct) == dict
    ## make list of dicts -------------------------------------------
    rows_list = []
    for ( row_num, row_data ) in rows_dct.items():
        assert type(row_data) == dict
        rows_list.append( row_data )
    log.debug( f'rows_list[0:10], ``{pprint.pformat(rows_list[0:10])}``' )
    ## validate each data-dict --------------------------------------
    validate_no_tabs( rows_list )  # raises exception if tab-character found
    validate_keys_same( rows_list )  # raises exception if keys differ
    validate_organization_id( rows_list )  # raises exception if org-id not found or is a list, or has a length of zero
    ## make subset list ---------------------------------------------
    subset_rows_list: list = make_subset_list( rows_list, sorted_target_orgs )
    sorted_subset_rows: list = sort_dicts_by_key( subset_rows_list, 'Organization ID' )
    ## make tsv file ------------------------------------------------
    write_tsv( sorted_subset_rows )
    return


## helper functions START -------------------------------------------


def make_starting_orgs_list() -> list:
    """ Makes list of orgs from STARTING_ORGS string.
        Adds '_' after the 'HH' prefix (turns 'HH123456' into 'HH_123456).
        Called by make_csv_from_fmpro_json() """
    target_orgs: list = []
    for org_id in STARTING_ORGS.split():
        updated_org_id: str = f'%s_%s' % ( org_id[0:2], org_id[2:] )
        target_orgs.append( updated_org_id )
    log.debug( f'target_orgs[0:10], ``{pprint.pformat(target_orgs[0:10])}``' )
    return target_orgs


def validate_no_tabs( rows_list: list ) -> None:
    """ Validates that there are no tab-characters in data.
        A tab-character might be ok, I just don't want to take a chance on the csv breaking.
        Raises exception if tab-character found.
        Called by make_csv_from_fmpro_json() """
    validity_flag: bool = True
    for row_data_dct in rows_list:
        for key_label, value in row_data_dct.items():
            # log.debug( f'key_label, ``{key_label}``; value, ``{value}``' )
            if value == None:
                # log.debug( 'value is None; continuing' )
                continue
            elif value == [None]:
                # log.debug( 'value is [None]; continuing' )
                continue
            if contains_tab_character( value ):
                log.warning( f'tab character found in key_label: {key_label}, value: {value}' )
                validity_flag = False
    log.debug( f'validity_flag, ``{validity_flag}``' )
    if validity_flag == False:
        msg = 'tab-character found in data; exiting'
        log.error( msg )
        raise Exception( msg )
    return


def contains_tab_character( value ) -> bool:
    """ Checks for tab-character in value, which can be a string or a list. 
        Called by validate_no_tabs() """
    assert type(value) in [ str, list ], type(value)
    if isinstance(value, str) and '\t' in value:
        log.debug( f'tab character found in value, ``{value}``' )
        return True
    if isinstance(value, list):
        rslt_check: bool = any( contains_tab_character(item) for item in value )
        if rslt_check:
            log.debug( f'tab character found in value, ``{value}``' )
        return rslt_check
    return False


def validate_keys_same( rows_list: list ) -> None:
    """ Checks that keys are the same.
        Raises exception if keys differ.
        Called by make_csv_from_fmpro_json() """
    first_item_keys = set(rows_list[0].keys())
    for index, item in enumerate(rows_list[1:], start=2): # start=2 for human-readable index
        if set(item.keys()) != first_item_keys:
            msg = 'item, ``{item}`` at index ``{index}`` does not have the same keys as the first item.'
            log.warning( msg )
            raise Exception( msg )
    else:
        log.debug( 'all items have the same keys.' )
    return


def validate_organization_id( rows_list: list ) -> None:
    """ Checks that each row has a valid organization-id.
        Raises exception if org-id not found or is a list, or has a length of zero.
        Called by make_csv_from_fmpro_json() """
    validity_flag: bool = True
    no_org_id_count: int = 0
    for i, row_data_dct in enumerate( rows_list ):
        org_id: str = row_data_dct['Organization ID']
        if org_id == None:
            # validity_flag = False
            log.warning( f'no org_id found for row_data_dct, ``{row_data_dct}``' )
            no_org_id_count += 1
            continue
        elif type(org_id) == list:
            validity_flag = False
        elif len(org_id) == 0:
            validity_flag = False
        if validity_flag == False:
            msg = f'problem with org_id, ``{org_id}`` at index ``{i}``; exiting'
            log.error( msg )
            raise Exception( msg )
    if no_org_id_count > 0:
        log.warning( f'no_org_id_count, ``{no_org_id_count}``' )
    else:
        log.debug( 'good; the no_org_id_count is 0' )
    log.debug( f'validity_flag, ``{validity_flag}``' )
    return


def make_subset_list( rows_list: list, sorted_target_orgs: list ) -> list:
    """ Makes a subset list of dicts -- for those dicts where the `Organization ID` value is in `sorted_target_orgs`.
        Called by make_csv_from_fmpro_json() """
    subset_rows_list: list = []
    for row_data_dct in rows_list:
        org_id: str = row_data_dct['Organization ID']
        if org_id in sorted_target_orgs:
            subset_rows_list.append( row_data_dct )
    log.debug( f'subset_rows_list[0:10], ``{pprint.pformat(subset_rows_list[0:10])}``' )
    return subset_rows_list


def sort_dicts_by_key( rows_list: list, key: str ) -> list:
    """ Sorts a list of dicts by the given key.
        Called by make_csv_from_fmpro_json() """
    sorted_rows_list = sorted( rows_list, key=lambda k: k[key] )
    log.debug( f'sorted_rows_list[0:10], ``{pprint.pformat(sorted_rows_list[0:10])}``' )
    return sorted_rows_list


def write_tsv( rows_list: list ) -> None:
    """ Creates a TSV file from a list of dictionaries.
        Writes to file.
        Called by make_csv_from_fmpro_json() """
    ## make path ----------------------------------------------------
    iso_now_time: str = datetime.datetime.now().isoformat()
    iso_now_time = iso_now_time.replace( ':', '-' )
    file_name: str = f'output_100_{iso_now_time}.tsv'  # to distinguish from `make_csv_rest.py` output
    file_path: str = f'../created_tsv_files/{file_name}'  # TODO -- take an output-path argument
    ## make and write file ------------------------------------------
    with open( file_path, 'w', newline='', encoding='utf-8' ) as file:
        writer = csv.DictWriter( file, fieldnames=rows_list[0].keys(), delimiter='\t' )
        writer.writeheader()
        for row in rows_list:
            for key in row:
                if row[key] is None:
                    row[key] = ''
            writer.writerow(row)
    log.debug( f'file written to file_path, ``{file_path}``' )
    return


## helper functions END ---------------------------------------------


## hardcoded org single string (from google-sheet) ------------------


STARTING_ORGS: str = """
HH010613
HH014131
HH003286
HH029529
HH002187
HH031509
HH013676
HH028689
HH002183
HH031510
HH008425
HH032303
HH031310
HH007258
HH025460
HH018840
HH018938
HH021482
HH026398
HH016818
HH026275
HH021633
HH001545
HH010471
HH017637
HH019947
HH021745
HH028521
HH025282
HH007174
HH019053
HH025113
HH027854
HH025204
HH011951
HH025201
HH024824
HH014832
HH030536
HH030652
HH027787
HH012400
HH016343
HH002379
HH011172
HH024122
HH027709
HH026949
HH008152
HH024272
HH013547
HH025336
HH026930
HH021933
HH018363
HH020197
HH024530
HH015484
HH025001
HH030119
HH030211
HH022227
HH019298
HH015473
HH024876
HH029867
HH024886
HH033381
HH005795
HH022778
HH002353
HH006786
HH019258
HH025005
HH025075
HH032229
HH025218
HH025328
HH030057
HH026435
HH027900
HH001645
HH008386
HH010729
HH015316
HH024969
HH025263
HH021916
HH025527
HH006344
HH024930
HH030510
HH012908
HH032287
HH005779
HH019456
HH022457
HH025087
HH025114
HH024904
"""


if __name__ == '__main__':
    ## set up argparser
    parser = argparse.ArgumentParser(description='Output CSV of given organization-IDs')
    parser.add_argument('--input_path', type=str, help='Path to big fmpro-export-json-file')
    args = parser.parse_args()
    log.debug( f'args: {args}' )
    ## get input path
    input_path = args.input_path if args.input_path else "../created_json_files/hhoag_data_as_of_2023-11-10.json"
    log.debug( f'input_path: {input_path}' )
    ## get to work
    make_csv_from_fmpro_json( input_path )
    log.debug( 'done' )