# Make a data ledger from code and data folders 

Here, we will make data descriptions (data url, name, description, etc.) from analyzing code and local data. 


```python

```


```python
# sources

code_folders= {
    'imbed_data_prep': __import__('imbed_data_prep').__path__[0],
}
data_folders = {
    'imbed_saves': "/Users/thorwhalen/Dropbox/_odata/app_data/imbed/saves",
    'figiri': "/Users/thorwhalen/Dropbox/_odata/figiri/"
}

```

# Extracting base urls from code

Make a function that will be given code (string) and figure out where the raw (seed) data is downloaded from.

Yeah, a pretty hard NLP problem. But now we have LLMs, so...

## Making the extractor


```python
import oa

refresh_json_schema = False


schema_description = """
    The output should include:
    * "url" field that points to the raw data source if there is only one source
    * "urls" (json object) field that is used when there are multiple sources for 
        various kinds of data is a json object where the keys are the names of the 
        data sources and the values are the urls
    * "url_type": (string) field that indicates the type of the url (e.g. "http", "file", "env_var", "config_key")
    * "name" (string) field that is a short name for the data set,
    * "description" (string) field that is a longer description of the data set
    * "parameters" (json object whose fields are names and values are descriptions) field
        that describe the different parameters that are used in the data preperation process 
    * "data_keys" (json object) fields which should indicate what kind of data artifacts 
        are created, or used in the data preperation process. This is often in the form of a 
        string that refers to a relative path, or other identifier.
    * "functions" (jso object) field containing python functions or methods that are 
        created in the data preperation process.
    """

if refresh_json_schema:
    print('Recomputing a json schema')
    from pprint import pprint

    json_schema = oa.tools.infer_schema_from_verbal_description(schema_description)

    print("--------------------")
    print(
        "Make sure to copy the following json schema into the code defining json_schema if you want to reuse it!!!"
    )
    print("--------------------")
    pprint(json_schema)


else:
    print('using cached json schema')
    json_schema = {
        'name': 'data_prep_code_analysis',
        'properties': {
            'name': {'type': 'string'},
            'url': {'type': 'string'},
            'url_type': {
                'enum': ['http', 'file', 'env_var', 'config_key'],
                'type': 'string',
            },
            'urls': {'additionalProperties': {'type': 'string'}, 'type': 'object'},
            'data_keys': {
                'additionalProperties': {'type': 'string'},
                'type': 'object',
            },
            'description': {'type': 'string'},
            'functions': {
                'additionalProperties': {'type': 'string'},
                'type': 'object',
            },
            'parameters': {
                'additionalProperties': {'type': 'string'},
                'type': 'object',
            },
        },
        'required': [
            'name',
            'url',
            'urls',
            'url_type',
            'description',
            'parameters',
            'data_keys',
            'functions',
        ],
        'type': 'object',
    }

analyze_data_prep_code = oa.prompt_json_function(
    f"""
    This python code should (but not necessarily) contain some data preperation code 
    that downloads some raw data and then processes it into a form that is ready for analysis.

    You should study the code and make a json object that describes the main "data feature" 
    that are therein: The data source, the data preparation artifacts, and the main 
    python functions, methods, or constants that the code creates.
    Note that sometimes the "url" or "urls" may not be actual http(s) urls, but could 
    also be filepaths, or the name(s) of environmental variables or configuration values
    (often in all caps) that are used to locate the url(s) of the data source(s).
    In this case, you should still use the "url" or "urls" fields, but the values should
    be strings that are not valid urls, but rather the name of the filepath, 
    the environmental variable or configuration key.

    Usually, if there is an http(s) url in the code, it is the main data source.

    Note though, that some inputs that are given may not be actual data prep code.

    In this case, you should just return an empty string for url and empty json objects 
    for urls, and in the description, you should indicate that this is not data prep code, 
    perhaps explaining why you think so. In this case start the description with 
    "NOT DATA PREP CODE", followed with your analysis/explication.

    {schema_description}

    {{python_code}}
    """,
    json_schema=json_schema,
)
```

    using cached json schema


## Gathering the code files we'll use


```python
def if_string_json_decode_it(x):
    if isinstance(x, str):
        import json 
        try:
            return json.loads(x)
        except:
            pass
    return x

def get_analysis_dict(code_key, py_file_contents):
    """Use this to extend the code_folders_analysis by doing
    code_folders_analysis.extend(get_analysis_dict(code_key, py_file_contents))
    or to replace an entry by doing
    code_folders_analysis[i] = get_analysis_dict(code_key, py_file_contents)
    """
    d = analyze_data_prep_code(py_file_contents)
    if 'result' in d:
        d['result'] = if_string_json_decode_it(d['result'])
    d['code'] = code_key
    return d

```


```python
import dol 
from collections import ChainMap
from pathlib import Path

exclude = {'arxiv.py', 'ultra_chat.py', 'embeddings_of_aggregations.py'}
PyStore = dol.Pipe(
    dol.TextFiles, 
    dol.filt_iter(
        filt=lambda x: x.endswith('py') and not x.startswith('_') and x not in exclude
    ),
)

s = PyStore(__import__('imbed_data_prep').__path__[0])
extra_files = {
    'xv.data_access': Path(__import__('xv').data_access.__file__).read_text(),
}

code_store = ChainMap(
    s,
    extra_files
)
list(code_store)
```




    ['xv.data_access',
     'prompt_injections.py',
     'wordnet_words.py',
     'hcp.py',
     'jersey_laws.py',
     'github_repos.py',
     'wildchat.py',
     'eurovis.py',
     'lmsys_ai_conversations.py',
     'twitter_sentiment.py']




```python
refresh_code_folders_analysis = False
code_folders_analysis_save_path = 'code_folders_analysis.json'
```


```python
import json 

if refresh_code_folders_analysis:
    
    def analyze_data_prep_code_of_folder(code_store, verbose=True):
        for code_key, py_file_contents in code_store.items():
            if verbose:
                print(f"  Analyzing {code_key}")
            yield get_analysis_dict(code_key, py_file_contents)
            
    code_folders_analysis = list(analyze_data_prep_code_of_folder(code_store))

    # sometimes the AI didn't manage to catch the urls, so we can manually add them here

    backup_urls = {
        'hcp.py': {
            'url': 'HCP_PUBS_SRC_KEY',
            'url_type': 'env_var',
        },
        'eurovis.py': {
            'url': 'https://81593031860c2ee4ad53a08892f7e95d.r2.cloudflarestorage.com/cosmograph/projects/eurovis/raw_data.csv',
            'url_type': 'http',
            # 'filepath': '/Users/thorwhalen/Dropbox/_odata/app_data/imbed/saves/eurovis/raw_data.csv'
        },
        # 'embeddings_of_aggregations.py': {"NOT A DATA PREP MODULE"}
    }


    for d in code_folders_analysis:
        if not d.get('url') and not d.get('urls'):
            if d['code'] in backup_urls:
                d.update(backup_urls[d['code']])

    json.dump(code_folders_analysis, open(code_folders_analysis_save_path, 'w'))

else:
    code_folders_analysis = json.load(open(code_folders_analysis_save_path))


print(f"{len(code_folders_analysis)} code folders analyzed")
[d['code'] for d in code_folders_analysis]

```

    10 code folders analyzed





    ['xv.data_access',
     'prompt_injections.py',
     'wordnet_words.py',
     'hcp.py',
     'jersey_laws.py',
     'github_repos.py',
     'wildchat.py',
     'eurovis.py',
     'lmsys_ai_conversations.py',
     'twitter_sentiment.py']




```python
len(code_folders_analysis)
```




    10




```python
code_folders_analysis_by_key = {d['code']: d for d in code_folders_analysis}
code_analysis_keys = list(code_folders_analysis_by_key)
code_analysis_keys
```




    ['xv.data_access',
     'prompt_injections.py',
     'wordnet_words.py',
     'hcp.py',
     'jersey_laws.py',
     'github_repos.py',
     'wildchat.py',
     'eurovis.py',
     'lmsys_ai_conversations.py',
     'twitter_sentiment.py']



# Extracting information from the folders


```python
data_folders = {
    'imbed_saves': "/Users/thorwhalen/Dropbox/_odata/app_data/imbed/saves",
    'figiri': "/Users/thorwhalen/Dropbox/_odata/figiri/"
}

```

## code_and_data_mapping


```python
import dol 

t = dol.FlatReader({k: dol.Files(path) for k, path in data_folders.items()})

pairs = {(x[0], x[1].split('/')[0]) for x in t}
data_folder_names = {x[1].split('/')[0] for x in t}
data_folder_names = sorted(
    filter(lambda x: not x.endswith(' alias') and not x.endswith('.parquet'), data_folder_names)
)
project_folders = {project_name: project_group for project_group, project_name in pairs}
data_folder_names
```




    ['eurovis',
     'github_repos',
     'harris_vs_trump',
     'hcp',
     'lmsys-chat-1m',
     'new_years_resolutions',
     'prompt-injections',
     'quotes',
     'spotify_playlists',
     'twitter_sentiment',
     'wildchat',
     'wordnet_words']




```python
refresh_code_and_data_matching = False

if refresh_code_and_data_matching:
    import oa

    f = oa.prompt_json_function(
        """
    Here's a list of data prep code files and a list of data folders.
                                
    Give me a json object that maps the data folders to the relevant code file
    that they use. Don't include those pairs that do not match.

    data_folders: {data_folders}    
    code_files: {code_files}
    """,
        # json_schema="the json schema could be just a json object with keys that are the "
        # "data folder names and values that are the code files",
    )

    code_and_data_mapping = f(data_folder_names, code_files=code_analysis_keys)['result']
else:
    code_and_data_mapping = {
        'eurovis': 'eurovis.py',
        'github_repos': 'github_repos.py',
        'hcp': 'hcp.py',
        'lmsys-chat-1m': 'lmsys_ai_conversations.py',
        'prompt-injections': 'prompt_injections.py',
        'twitter_sentiment': 'twitter_sentiment.py',
        'wildchat': 'wildchat.py',
        'wordnet_words': 'wordnet_words.py',
    }

code_and_data_mapping
```




    {'eurovis': 'eurovis.py',
     'github_repos': 'github_repos.py',
     'hcp': 'hcp.py',
     'lmsys-chat-1m': 'lmsys_ai_conversations.py',
     'prompt-injections': 'prompt_injections.py',
     'twitter_sentiment': 'twitter_sentiment.py',
     'wildchat': 'wildchat.py',
     'wordnet_words': 'wordnet_words.py'}




```python
_remaining_code_names = sorted(set(code_analysis_keys) - set(code_and_data_mapping.values()))
_remaining_data_folders = sorted(set(data_folder_names) - set(code_and_data_mapping.keys()))
_remaining_data_folders, _remaining_code_names
```




    (['harris_vs_trump', 'new_years_resolutions', 'quotes', 'spotify_playlists'],
     ['jersey_laws.py', 'xv.data_access'])




```python
# just to test
assert project_folders['wildchat'] == 'imbed_saves'
```

## gather information for each project


```python
import dol 
import os 

def code_and_data_files(name):
    project_group = project_folders[name]
    project_folderpath = os.path.join(data_folders[project_group], name)
    t = dol.filt_iter(
        dol.Files(project_folderpath, max_levels=0),
    )
    data_filepaths = [os.path.join(project_folderpath, fn) for fn in t]
    data_filepaths = sizes_of_files_paths(data_filepaths)
    data_filenames = list(map(os.path.basename, data_filepaths))

    d = dict(
        project_group=project_group, 
        data_filenames=data_filenames,
        data_filepaths=data_filepaths
    )

    code_file = code_and_data_mapping.get(name, None)
    if code_file:
        d.update(code_file=code_file, code_contents=code_store[code_file])
        
    return d

def sizes_of_files_paths(filepaths):
    import os 
    sizes = {fp: os.path.getsize(fp) for fp in filepaths}
    # sort by size
    sizes = dict(sorted(sizes.items(), key=lambda x: x[1]))
    return sizes

# test
t = code_and_data_files('hcp')
list(t)

```




    ['project_group',
     'data_filenames',
     'data_filepaths',
     'code_file',
     'code_contents']




```python
def table_info(filepath):
    import tabled

    try:
        df = tabled.get_table(filepath)
        return dict(
            shape=df.shape,
            first_row=df.iloc[0],
        )
    except:
        return None


problematic_files = tuple(
    [
        '/Users/thorwhalen/Dropbox/_odata/app_data/imbed/saves/wildchat/embeddings.parquet',
    ]
)


def gather_info_for_name(name, skip=problematic_files, verbose=True):
    _clog = clog(verbose)
    _clog(f"Getting info for {name}")
    d = code_and_data_files(name)
    d['num_of_data_files'] = len(d['data_filepaths'])

    def tables_info():
        for filepath in d['data_filepaths']:
            if filepath in skip:
                _clog("     ---> Skipping", filepath)
                continue
            _clog("   Getting table info for", filepath)
            yield os.path.basename(filepath), table_info(filepath)

    d['tables_info'] = dict(tables_info())
    return d


from tabled import pandas_json_dumps
import dol
from functools import partial
from lkj import clog


JsonFiles = dol.wrap_kvs(
    dol.TextFiles, 
    value_encoder=partial(pandas_json_dumps, indent=2), 
    value_decoder=json.loads,
    key_codec=dol.KeyCodecs.suffixed(suffix='.json')
)

# json_store = dol.mk_dirs_if_missing(JsonFiles('data_folders_info'))
project_info_store = dol.add_missing_key_handling(
    dol.mk_dirs_if_missing(JsonFiles('data_folders_info')),
    missing_key_callback=lambda store, k: gather_info_for_name(k),
)

    
```
