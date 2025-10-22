"""
Base functionality of cosmodata

"""


def ensure_installed(packages, pip_names=None, quiet=True):
    """
    Ensure packages are installed, installing if missing.

    Supports space-separated package strings and version specs.
    Interactive confirmation locally, auto-install in Colab.

    Args:
        packages: Space-separated string or list of package specs
                  Examples: 'graze tabled pandas'
                           ['graze>=0.1.0', 'tabled', 'pandas<2.0']
        pip_names: Dict mapping import names to pip names
                   Example: {'PIL': 'Pillow', 'cv2': 'opencv-python'}
        quiet: Suppress pip output (default True)

    Examples:

    >>> ensure_installed('graze tabled pandas')  # doctests: +SKIP
    >>> ensure_installed(['graze>=0.1.0', 'tabled', 'pandas<2.0'])  # doctests: +SKIP
    >>> ensure_installed('PIL cv2', pip_names={'PIL': 'Pillow', 'cv2': 'opencv-python'})  # doctests: +SKIP

    """
    import sys
    import subprocess
    import importlib
    import re
    from packaging import version

    # Handle space-separated string
    if isinstance(packages, str):
        packages = packages.split()

    pip_names = pip_names or {}

    # Detect Colab
    try:
        import google.colab

        in_colab = True
    except ImportError:
        in_colab = False

    # Parse package specs: 'pkg>=1.0' -> ('pkg', '>=', '1.0')
    def parse_spec(spec):
        match = re.match(r'^([a-zA-Z0-9_-]+)\s*([><=]+)?\s*([\d.]+)?', spec)
        if match:
            pkg, op, ver = match.groups()
            return pkg, op, ver
        return spec, None, None

    missing = []

    for spec in packages:
        pkg_name, op, required_ver = parse_spec(spec)
        import_name = pkg_name.replace('-', '_')  # pip name -> import name

        try:
            mod = importlib.import_module(import_name)

            # Check version if specified
            if op and required_ver:
                current_ver = getattr(mod, '__version__', None)
                if current_ver:
                    satisfied = _check_version(current_ver, op, required_ver)
                    if not satisfied:
                        pip_spec = pip_names.get(pkg_name, spec)  # Use full spec
                        missing.append(pip_spec)
                else:
                    # Can't verify version, assume it needs update
                    missing.append(pip_names.get(pkg_name, spec))
        except ImportError:
            pip_spec = pip_names.get(pkg_name, spec)
            missing.append(pip_spec)

    if not missing:
        return

    # Ask for permission locally, auto-install in Colab
    if not in_colab:
        print(f"📦 The following packages will be installed: {', '.join(missing)}")
        response = input("Continue? [Y/n]: ").strip().lower()
        if response and response not in ('y', 'yes'):
            print("Installation cancelled.")
            return

    # Install missing packages
    cmd = [sys.executable, '-m', 'pip', 'install']
    if quiet:
        cmd.append('-q')
    cmd.extend(missing)

    print(f"📦 Installing: {', '.join(missing)}")
    subprocess.check_call(cmd)
    print("✓ Installation complete")


def _check_version(current, op, required):
    """Check if version satisfies requirement."""
    from packaging import version

    curr = version.parse(current)
    req = version.parse(required)

    if op == '>=':
        return curr >= req
    elif op == '>':
        return curr > req
    elif op == '<=':
        return curr <= req
    elif op == '<':
        return curr < req
    elif op == '==':
        return curr == req
    return True  # No op means any version OK


import os
import shutil
from collections.abc import Mapping

if os.name == 'nt':
    win_base = os.environ.get('APPDATA')
    if not win_base:
        win_base = os.path.join(os.path.expanduser('~'), 'AppData', 'Local')
    DFLT_CACHE_DIR = os.path.join(win_base, 'cosmodata', 'datasets')
else:
    DFLT_CACHE_DIR = os.path.expanduser('~/.local/share/cosmodata/datasets')


from cosmodata.util import graze, url_to_file_download
from functools import partial
import tabled


def acquire_data(
    src,
    cache_key=None,
    *,
    getter=None,
    refresh=False,
    cache_dir=None,
    ext=None,
):
    """
    Acquire data from source with automatic caching (Colab-aware).

    Intelligently caches to Google Drive in Colab or local disk otherwise.
    Auto-detects appropriate getter for URLs and files.

    Args:
        src: Source (URL, filepath, or anything getter can process)
        getter: Function(src) -> data. If None, auto-detects (graze/tabled/requests)
        cache_key: Cache identifier. If None, generates hash from src
        refresh: If True, bypass cache and re-fetch data
        cache_dir: Cache directory. If None, uses Drive in Colab or ~/.data_cache locally

    Returns:
        The acquired data

    Examples:

        # Simple URL to DataFrame (auto-cached)
        df = acquire_data('https://example.com/data.csv')

        # Custom getter with named cache
        data = acquire_data(
            'https://api.example.com/data',
            getter=lambda url: requests.get(url).json(),
            cache_key='api_data'
        )

        # Force refresh cached data
        df = acquire_data(url, refresh=True)
    """
    import os
    import pickle
    from urllib.parse import urlparse
    from pathlib import Path
    from hashlib import md5

    # Detect Colab and setup cache directory
    try:
        # Note: Don't install locally - it doesn't work outside colab
        import google.colab
        from google.colab import drive

        if cache_dir is None:
            drive_path = '/content/drive'
            if not os.path.exists(f'{drive_path}/MyDrive'):
                print("Mounting Google Drive...")
                drive.mount(drive_path)
            cache_dir = f'{drive_path}/MyDrive/.colab_cache'
    except ImportError:
        # Local execution (not in Colab)
        if cache_dir is None:
            cache_dir = os.path.expanduser('~/.local/share/cosmodata/datasets')

    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)

    if cache_key is None:
        cache_key = md5(str(src).encode()).hexdigest()[:16]

    ext = _normalize_ext(ext)

    cache_path = cache_dir / cache_key
    if ext:
        cache_file = cache_path.with_suffix(f'.{ext}')
    elif cache_path.suffix:
        cache_file = cache_path
        ext = _normalize_ext(cache_file.suffix)
    else:
        cache_file = cache_path.with_suffix('.pkl')

    file_cache = cache_file.suffix != '.pkl'
    pickle_cache_file = (
        cache_file if cache_file.suffix == '.pkl' else cache_path.with_suffix('.pkl')
    )

    def default_loader(target):
        target = str(target)
        if ext:
            return tabled.get_table(target, ext=ext)
        return tabled.get_table(target)

    def call_loader(target):
        if getter is not None:
            try:
                return getter(str(target))
            except TypeError:
                return default_loader(target)
        return default_loader(target)

    def load_cached_file():
        return call_loader(cache_file)

    def is_url(value):
        if not isinstance(value, str):
            return False
        parsed = urlparse(value)
        return parsed.scheme in ('http', 'https')

    def download_or_copy_source():
        if not isinstance(src, str):
            return False
        if is_url(src):
            overwrite = True if refresh else False
            try:
                url_to_file_download(src, filepath=str(cache_file), overwrite=overwrite)
                return True
            except Exception as e:
                print(f"Warning: Could not download {src}: {e}")
                return False
        src_path = Path(src)
        if src_path.exists():
            try:
                if src_path.resolve() != cache_file.resolve():
                    cache_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src_path, cache_file)
                else:
                    cache_file.parent.mkdir(parents=True, exist_ok=True)
                return True
            except Exception as e:
                print(f"Warning: Could not copy {src_path} to cache: {e}")
        return False

    def store_data_to_file(data):
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        suffix = cache_file.suffix.lower()
        try:
            if isinstance(data, (bytes, bytearray)):
                cache_file.write_bytes(data)
                return True
            if isinstance(data, str):
                cache_file.write_text(data)
                return True
            if suffix in ('.parquet', '.feather') and hasattr(data, 'to_parquet'):
                data.to_parquet(cache_file)
                return True
            if suffix in ('.csv', '.tsv', '.txt') and hasattr(data, 'to_csv'):
                sep = '\t' if suffix == '.tsv' else ','
                data.to_csv(cache_file, index=False, sep=sep)
                return True
            if suffix == '.json' and hasattr(data, 'to_json'):
                data.to_json(cache_file, orient='records')
                return True
            if suffix in ('.pkl', '.pickle'):
                with open(cache_file, 'wb') as f:
                    pickle.dump(data, f)
                return True
        except Exception as e:
            print(f"Warning: Could not serialize data to {cache_file}: {e}")
        return False

    def try_file_cache():
        cache_file.parent.mkdir(parents=True, exist_ok=True)

        if refresh and cache_file.exists():
            cache_file.unlink(missing_ok=True)

        if not refresh and cache_file.exists():
            try:
                return True, load_cached_file()
            except Exception as e:
                print(f"Cache read failed: {e}, refreshing cache...")
                cache_file.unlink(missing_ok=True)

        fetched = download_or_copy_source()
        if fetched and cache_file.exists():
            try:
                return True, load_cached_file()
            except Exception as e:
                print(f"Warning: Failed to load cached file {cache_file}: {e}")

        data = call_loader(src)
        if store_data_to_file(data):
            return True, data
        return False, data

    def cache_with_pickle(prefetched=None):
        pickle_cache_file.parent.mkdir(parents=True, exist_ok=True)
        if refresh and pickle_cache_file.exists():
            pickle_cache_file.unlink(missing_ok=True)

        if not refresh and pickle_cache_file.exists():
            try:
                with open(pickle_cache_file, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                print(f"Cache read failed: {e}, fetching fresh data...")
                pickle_cache_file.unlink(missing_ok=True)

        data = prefetched if prefetched is not None else call_loader(src)
        try:
            with open(pickle_cache_file, 'wb') as f:
                pickle.dump(data, f)
        except Exception as e:
            print(f"Warning: Could not cache data at {pickle_cache_file}: {e}")
        return data

    prefetched = None
    if file_cache:
        success, prefetched = try_file_cache()
        if success:
            return prefetched

    return cache_with_pickle(prefetched=prefetched)


acquire_data.DFLT_CACHE_DIR = DFLT_CACHE_DIR


# --------------------------------------------------------------------------------------
# Stores
import dol
from cosmodata.util import meta_files_rootdir

# Store of metadata files
metas = dol.wrap_kvs(
    dol.JsonFiles(meta_files_rootdir), key_codec=dol.KeyCodecs.suffixed(".json")
)


def _try_various_fields_until_found(meta, fields):
    for field in fields:
        if field in meta:
            return meta[field]
    return None


def _data_src_from_meta(meta, fields=('url',)):
    return _try_various_fields_until_found(meta, fields)


def _assign_if_not_none(target, target_key, src, src_keys):
    if isinstance(src_keys, str):
        src_keys = (src_keys,)
    for key in src_keys:
        if key in src:
            target[target_key] = src[key]
            return


def _normalize_ext(ext):
    if not ext:
        return None
    return ext.lstrip('.')


def _cache_key_from_meta(meta):
    for field in ('cache_key', 'target_filename', 'output_filename', 'slug'):
        value = meta.get(field)
        if value:
            return value
    return None


def _infer_ext(meta, current_ext=None):
    ext = current_ext or meta.get('ext') or meta.get('extension')
    if not ext and meta.get('target_filename'):
        ext = os.path.splitext(meta['target_filename'])[1]
    return ext


def _get_acquire_data_kwargs(meta):
    if not isinstance(meta, Mapping):
        raise TypeError(f"Expected metadata mapping, got {type(meta)!r}")
    kws = {}
    _assign_if_not_none(kws, 'src', meta, 'src')
    if 'src' not in kws:
        raise KeyError("Metadata entry is missing mandatory 'src'")
    cache_key = _cache_key_from_meta(meta)
    if cache_key:
        kws['cache_key'] = cache_key
    ext = _infer_ext(meta)
    if ext:
        kws['ext'] = ext
    if meta.get('cache_dir'):
        kws['cache_dir'] = meta['cache_dir']
    if meta.get('refresh') is not None:
        kws['refresh'] = meta['refresh']
    return kws


def _meta_to_data(meta, getter=_get_acquire_data_kwargs):
    kws = getter(meta)
    ext = kws.get('ext')
    if ext is not None:
        ext = _normalize_ext(ext)
        kws['ext'] = ext
    if ext:
        getter = partial(tabled.get_table, ext=ext)
    else:
        getter = tabled.get_table
    return acquire_data(**kws, getter=getter)


def _datas_value_encoder(meta):
    if not isinstance(meta, Mapping):
        return meta
    meta = dict(meta)
    cache_key = meta.get('cache_key')
    target_filename = meta.get('target_filename')
    if target_filename:
        meta.setdefault('cache_key', target_filename)
        inferred_ext = _infer_ext(meta)
        if inferred_ext and not meta.get('ext'):
            meta['ext'] = inferred_ext
    return meta


# Store of tables (acquired and cached)
datas = dol.wrap_kvs(metas, value_decoder=_meta_to_data, value_encoder=_datas_value_encoder)
datas.graze_root = graze.rootdir
