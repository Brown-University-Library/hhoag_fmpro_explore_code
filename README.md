# Purpose

Code we can use to experiment with parsing hall-hoag xml. 

'Usage' notes below assume a virtual-environment has been activated.

---

## make_csv_100.py

Takes the source json-file produced by `convert_fmproxml_to_json.py` and outputs a TSV file. In this case, it produces a subset of all the items in the json file due to a requirement to only produced data for a preset list of orgs.

Notes
- though a `csv` was specified, the data contains lots of commas, so after confirming the data doesn't contain tab-characters, I decided to produce a `tsv` file instead.
- the output file will not overwrite previous output files -- because a timestamp is included in the filename.
- TODO: the output file is hard-coded to go to a '../created_tsv_files/' dir; add an output-path argument.

__Usage:__
```
(venv) $ python ./make_csv_100.py --input_path "/path/to/file.json"
```

---


## convert_fmproxml_to_json.py

Converts exported filemaker-pro xml to json.

The exported filemaker-pro xml is hard to read because, like a CSV, it has a 'row' of headings; the rest is data. And all data-elements are bounded simply by the `<DATA>` element, so it's hard to work with programmatically. This turns the exported data into nicely-viewable, and programmatically accessible, key-value pairs.

Though the meat of the output is the 'items' data, the output-dict has a `__meta__` key, containing potentially useful info such as the number-of-items, and number of non-unique "Record ID" values.

_(Note: this code is based on old [ball-gallery](https://github.com/Brown-University-Library/bell) code; some of the code-comments still reference that older code.)_

__Usage:__
```
(venv) $ python ./convert_fmproxml_to_json.py --input_path "/path/to/source.xml" --output_path "/path/to/output.json"
```

`test_convert_xml.py` is a test for one of this file's functions.

__Usage:__
```
(venv) $ python ./test_convert_xml.py
```

---


## unique_orgs.py

Goes through exported xml and lists unique organizations, with an item-count for each. Note that the 'items' appear to be boxes.

__Usage:__
```
(venv) $ python ./unique_orgs.py --input_path "/path/to/source.xml"
```

---


## pretty_print.py

Simply takes the raw filemaker-pro export (which is all on one or two lines), and formats it.

Note: Automatically outputs the formatted-file in the same directory, with the filename "original_filename_formatted.xml"

__Usage:__
```
(no venv needed) $ python ./pretty_print.py --input_path "/path/to/source.xml"
```

---
