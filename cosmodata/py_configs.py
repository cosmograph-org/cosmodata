"""A module that contains python configurations.

Normally, a configration file would be written in a platform independent language
(such as ini, csv, json, yaml, or toml) that expresses a mapping from a string key to
some value for that key, which could itself be a mapping.

Here it is very much the same situation, but the values are python objects.
More precisely, the first level keys are python-valid identifiers, and the values are
either python objects or some mapping that will eventually result in leaf values.

This module is for the convenience the python developer who wants to provide a python
configuration for a data source. If one wants to make things more platform independent,
though, they had better write the configs in a platform independent language and
load it and interpret into python (or whatever the target language is).

"""

from cosmodata.util import (
    Pipe, url_to_first_zipped_file_bytes, load_matlab_bytes
)

val_trans_for_name = {
    "amazon-fraud": Pipe(url_to_first_zipped_file_bytes, load_matlab_bytes),
    "yelp-fraud": Pipe(url_to_first_zipped_file_bytes, load_matlab_bytes),
}

