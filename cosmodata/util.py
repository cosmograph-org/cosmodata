"""Utils"""

import os
import i2
import dol
from importlib_resources import files
from functools import partial


def get_package_name():
    """Return current package name"""
    # return __name__.split('.')[0]
    # TODO: See if this works in all cases where module is in highest level of package
    #  but meanwhile, hardcode it:
    return "cosmodata"


# get app data dir path and ensure it exists
pkg_name = get_package_name()
# _root_app_data_dir = i2.get_app_data_folder()
# app_data_dir = os.environ.get(
#     f"{pkg_name.upper()}_APP_DATA_DIR",
#     os.path.join(_root_app_data_dir, pkg_name),
# )
# dol.ensure_dir(app_data_dir, verbose=f"Making app dir: {app_data_dir}")


repo_stub = f"cosmograph-org/{pkg_name}"
proj_files = files(pkg_name)
links_files = proj_files / "links"
link_files_rootdir = str(links_files)
branch = "master"
content_url = (
    f"https://raw.githubusercontent.com/{repo_stub}/" + branch + "/{}"
).format


def get_content_bytes(key, max_age=None):
    """Get bytes of content from `cosmograph-org/cosmodata`, auto caching locally.

    ```
    # add max_age=1e-6 if you want to update the data with the remote data
    b = get_content_bytes('tables/csv/projects.csv', max_age=None)
    ```
    """
    return graze(content_url(key), max_age=max_age)


def get_table(key, max_age=None, *, file_type=None, **extra_pandas_kwargs):
    """Get pandas dataframe from `cosmograph-org/cosmodata`, auto caching locally.
    ```
    # add max_age=1e-6 if you want to update the data with the remote data
    t = get_table('links/fraud.csv', max_age=None)
    ```
    """
    b = get_content_bytes(key, max_age=max_age)
    file_type = file_type or key.split(".")[-1]

    if file_type == "csv":
        return pd.read_csv(io.BytesIO(b), **extra_pandas_kwargs)
    elif file_type == "md":
        return pd.read_csv(io.BytesIO(b), **dict(extra_pandas_kwargs, sep="|"))
    elif file_type == "json":
        return pd.read_json(io.BytesIO(b), **extra_pandas_kwargs)
    elif file_type == "xlsx":
        return pd.read_excel(io.BytesIO(b), **extra_pandas_kwargs)
    else:
        raise ValueError(f"Unknown file type for {key}")


# --------------------------------------------------------------------------------------


import io
import os
from operator import itemgetter

# from functools import partial

import pandas as pd

from graze import graze
from i2 import Pipe
from i2.routing_forest import KeyFuncMapping
from dol import FilesOfZip
from dol import Files, wrap_kvs, add_ipython_key_completions

# from cosmodata.util import links_files

#
# def link_postget(k, v):
#     df_from_data_according_to_key(v, )


def no_route_found_error(obj):
    raise ValueError(f"No route found for {obj}")


get_ext = Pipe(os.path.splitext, itemgetter(-1))


def clean_table(df):
    # strip columns of whitespace
    df.columns = df.columns.str.strip()
    # strip whitespace from all strings
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    return df


prepper = KeyFuncMapping(
    {
        ".csv": Pipe(io.BytesIO, pd.read_csv, clean_table),
        ".xls": Pipe(io.BytesIO, pd.read_excel, clean_table),
        ".json": Pipe(io.BytesIO, pd.read_json, clean_table),
    },
    key=get_ext,
    default_factory=no_route_found_error,
)


def keyed_trans(k, v, key_to_trans=prepper):
    return key_to_trans(k)(v)


def get_data(url, prepper=prepper):
    b = graze(url)
    trans = prepper(url)
    return trans(b)


@add_ipython_key_completions
@wrap_kvs(postget=keyed_trans)
class LinkFileTables(Files):
    """Store of link files (which contain data names, urls, and other info)"""
    def __init__(self, rootdir=link_files_rootdir, **kwargs):
        super().__init__(rootdir, **kwargs)

from typing import Callable, Mapping, NewType

Name = NewType("Name", str)
Url = NewType("Url", str)
NameUrlMapping = Mapping[Name, Url]


def df_to_simple_dict(key_col, val_col, df):
    return df.set_index(key_col)[val_col].to_dict()


to_name_and_url_dict = partial(df_to_simple_dict, "name", "url")


# TODO: add a way to still access the other information contained in the table.
#   For example, using StringWhereYouCanAddAttrs (in plunk) or a store with a meta attr
#   See https://github.com/i2mint/py2store/issues/58#issuecomment-1448208488
@add_ipython_key_completions
@wrap_kvs(obj_of_data=to_name_and_url_dict)
class LinkFileMapping(LinkFileTables):
    """"""


# --------------------------------------------------------------------------------------

import io
from collections import defaultdict
# from functools import partial

import graze
from dol import Pipe, wrap_kvs, Store
from operator import methodcaller

# TODO: Could use cosmodata specific graze persistence folder here, or give user choice
_graze = partial(graze.graze, preget=graze.preget_print_downloading_message)
store_egress = add_ipython_key_completions


def next_asserting_uniqueness(iterator):
    v = next(iterator)
    assert next(iterator, None) is None, "There was more than one value in iterator"
    return v


# TODO: Add default here once https://github.com/i2mint/dol/issues/9 is fixed
def postget_factory(val_trans_for_name, k, v):
    if k in val_trans_for_name:
        value_transformer = val_trans_for_name[k]
        return value_transformer(v)
    return v


# TODO: Add a default (make it be _graze?)
def info_df_to_data_store(
    info_df,
    val_trans_for_name=(),
    *,
    default_val_trans=_graze,
    name_col="name",
    url_col="url",
):
    """Transforms a link store into a data store.
    A link store url values that are given names (the keys).
    A data store has the same keys (data names) but the values are the data.

    In order to get from the url to the data, a val_trans_for_name specification of
    how to transform each value must be provided.
    """
    if name_col is not None:
        info_df = info_df.set_index(name_col)
    # else we'll take the keys of the df as the names
    link_store = info_df[url_col].to_dict()

    # TODO: Add default in postget_factory instead.
    val_trans_for_name = defaultdict(
        lambda: default_val_trans, **dict(val_trans_for_name)
    )
    link_to_data_store_trans = Pipe(
        wrap_kvs(postget=partial(postget_factory, val_trans_for_name)),
    )
    data_store = store_egress(link_to_data_store_trans(link_store))
    data_store.meta = store_egress(Store(info_df.to_dict(orient='index')))
    return data_store


first_value = Pipe(methodcaller("values"), iter, next_asserting_uniqueness)
url_to_first_zipped_file_bytes = Pipe(_graze, FilesOfZip, first_value)


def load_matlab_bytes(b):
    from scipy.io import loadmat

    return loadmat(io.BytesIO(b))  # type: ignore
