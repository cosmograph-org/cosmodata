"""Utils"""

import os
import i2
import dol
from typing import Callable
from importlib_resources import files
from functools import partial
import graze as _graze
import pandas as pd


def get_package_name():
    """Return current package name"""
    # return __name__.split('.')[0]
    # TODO: See if this works in all cases where module is in highest level of package
    #  but meanwhile, hardcode it:
    return "cosmodata"


# get app data dir path and ensure it exists
pkg_name = get_package_name()
_root_app_data_dir = i2.get_app_data_folder()
app_data_dir = os.environ.get(
    f"{pkg_name.upper()}_APP_DATA_DIR",
    os.path.join(_root_app_data_dir, pkg_name),
)
grazed_data_dir = os.path.join(app_data_dir, "grazed")
dol.ensure_dir(app_data_dir, verbose=f"Making app dir: {app_data_dir}")
dol.ensure_dir(app_data_dir, verbose=f"Making grazed dir: {grazed_data_dir}")

graze = partial(
    _graze.graze,
    rootdir=grazed_data_dir,
    key_ingress=_graze.graze.key_ingress_print_downloading_message,
)

url_to_file_download = partial(
    _graze.url_to_file_download,
    rootdir=grazed_data_dir,
    overwrite=False,
)

repo_stub = f"cosmograph-org/{pkg_name}"
proj_files = files(pkg_name)
base_groups_files = proj_files / "groups"
base_groups_files_rootdir = str(base_groups_files)

from typing import Iterable, Mapping
import dol
import tabled

# Field (column) names with specific semantics (and operations)
_data_sources_columns = {
    'name': 'name of data (preferably unique, so can be used as key)',
    'url': (
        'url from which data can be downloaded. '
        'This could really be anything that url_to_local_path function can handle.'
    ),
    'filepath': 'path to file in local system where data can be found (often downloaded from url)',
    'info_url': 'url from which more information about data can be downloaded',
    'info_filepath': 'path to file in local system where info can be found',
    'group': 'group to which data belongs',
    'description': 'description of the data',
}
data_sources_columns = tuple(_data_sources_columns)


def data_sources_df(link_tables: Iterable):
    if isinstance(link_tables, Mapping):
        link_tables_mapping = link_tables
        link_tables = link_tables_mapping.items()

    def tables_with_group():
        for group, link_table in link_tables:
            link_table.columns = link_table.columns.str.strip()
            if 'group' not in link_table.columns:
                link_table['group'] = group
            yield link_table

    aggregate_df = pd.concat(tables_with_group(), ignore_index=True)
    aggregate_df = tabled.ensure_columns(aggregate_df, data_sources_columns)
    aggregate_df = tabled.ensure_first_columns(aggregate_df, data_sources_columns)
    # fill missing values with None
    aggregate_df = aggregate_df.where(pd.notnull(aggregate_df), None)
    return aggregate_df[list(data_sources_columns)]


def data_sources_df_from_filespaths(link_tables_filepaths):
    """Get a dataframe of data sources from a collection of link tables"""

    def key_and_table():
        for k in link_tables_filepaths:
            try:
                yield k, tabled.get_table(k)
            except Exception as e:
                print(f"Error with {k}: {e}")

    return data_sources_df(key_and_table())


# TODO: Could move this to tabled or lkj?
def resolve_fields(
    iterable,
    resolution_dict: dict,
    needs_resolution: Callable = lambda x, field: x.get(field, None) is None,
):
    for x in iterable:
        for field, resolution_func in resolution_dict.items():
            if needs_resolution(field):
                x[field] = resolution_func(x)


link_table_resulution_dict = {}


def get_data_sources_df(link_filepaths=None):
    link_filepaths = dol.filesys.FileBytesReader(base_groups_files_rootdir)
    return data_sources_df_from_filespaths(link_filepaths)


# --------------------------------------------------------------------------------------


import io
import os
from operator import itemgetter

# from functools import partial

import pandas as pd

from i2 import Pipe
from i2.routing_forest import KeyFuncMapping
from dol import FilesOfZip
from dol import Files, wrap_kvs, add_ipython_key_completions

# from cosmodata.util import base_groups_files

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
    df = df.map(lambda x: x.strip() if isinstance(x, str) else x)
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

    def __init__(self, rootdir=base_groups_files_rootdir, **kwargs):
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

from dol import Pipe, wrap_kvs, Store
from operator import methodcaller

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


def info_df_to_data_store(
    info_df,
    val_trans_for_name=(),
    *,
    default_val_trans=graze,
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
url_to_first_zipped_file_bytes = Pipe(graze, FilesOfZip, first_value)


def load_matlab_bytes(b):
    from scipy.io import loadmat

    return loadmat(io.BytesIO(b))  # type: ignore


# --------------------------------------------------------------------------------------
# WIP


def update_base_with_local(
    base_df: pd.DataFrame, local_df: pd.DataFrame
) -> pd.DataFrame:
    """
    This function "merges" the
    * base_df (specific to the package) and the
    * local_df (specific to the user)

    Both dfs MUST contain a url column:
    * url: the url (or URI) from which the data can be downloaded. This could really be
    anything that the url_to_local_path function can handle.

    The following columns are optional, but have specific meanings (and operations):
    * filepath: path to file in local system where data can be found (often downloaded from url)
    * name: name of data (preferably unique, so can be used as key)
    * info_url: url from which more information about data can be downloaded
    * info_filepath: path to file in local system where info can be found
    * group: group to which data belongs
    * description: description of the data

    local_df's information takes precedence over base_df's information.
    
    The purpose of base_df is to "seed" local_df. 

    More precisely, base_df and local_df will be aligned, merging over the url column.
    The rows corresponding to urls that are in one, but not the other, will be added
    (at the end).

    """
    pass


# --------------------------------------------------------------------------------------
# getting tables from raw github urls (only mentioning repo_stub)
# TODO: Old stuff (perhaps remove --> but make sure it's logged somewhere, because it's good!)

branch = "master"
content_url = (
    f"https://raw.githubusercontent.com/{repo_stub}/" + branch + "/{}"
).format


def get_content_bytes_from_raw_github(key, max_age=None):
    """Get bytes of content from `cosmograph-org/cosmodata`, auto caching locally.

    ```
    # add max_age=1e-6 if you want to update the data with the remote data
    b = get_content_bytes('tables/csv/projects.csv', max_age=None)
    ```
    """

    return graze(content_url(key), max_age=max_age)


def get_table_from_raw_github(
    key, max_age=None, *, file_type=None, **extra_pandas_kwargs
):
    """Get pandas dataframe from `cosmograph-org/cosmodata`, auto caching locally.
    ```
    # add max_age=1e-6 if you want to update the data with the remote data
    t = get_table('groups/fraud.csv', max_age=None)
    ```
    """
    b = get_content_bytes_from_raw_github(key, max_age=max_age)
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
