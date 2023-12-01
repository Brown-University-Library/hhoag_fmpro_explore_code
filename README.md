# Purpose

Code we can use to experiment with parsing hall-hoag xml. 

All 'usage' notes below assume a virtual-environment has been activated.

---


### convert_fmproxml_to_json.py

Converts exported filemaker-pro xml to json.

The exported filemaker-pro xml is hard to read because, like a CSV, it has a 'row' of headings; the rest is data. And all data-elements are bounded simply by the <DATA> element, so it's hard to work with programmatically. This turns the exported data into nicely-viewable, and programmatically accessible, key-value pairs.

Though the meat of the output is the 'items' data, the output-dict has a __meta__ key, containing potentially useful info such as the number-of-items, and duplicate "Record ID" info.

Usage:
```
(venv) $ python ./convert_fmproxml_to_json.py --input_path "/path/to/source.xml" --output_path "/path/to/output.json"
```

`test_convert_xml.py` is a test for one of this file's functions.

Usage:
```
(venv) $ python ./test_convert_xml.py
```

---


### unique_orgs.py

Goes through exported xml and lists unique organizations, with an item-count for each. Note that the 'items' appear to be boxes.

Usage:
```
(venv) $ python ./unique_orgs.py --input_path "/path/to/source.xml"
```

---
