# cosmodata

A portal to data sources for cosmograph

To install:	```pip install cosmodata```


# Datasets Overview

## Introduction
This repository contains datasets for various projects, each prepared for visualization and analysis using Cosmograph. The raw data consists of structured information from sources like academic publications, GitHub repositories, political debates, and Spotify playlists. The prepared datasets feature embeddings and 2D projections that enable scatter and force-directed graph visualizations.

## Dataset Descriptions


### EuroVis Dataset
- **Raw Data:** Academic publications metadata from the EuroVis conference, including titles, abstracts, authors, and awards.
- **Prepared Data:** [merged_artifacts.parquet](https://www.dropbox.com/scl/fi/i285q892wjmm6f9oak41g/merged_artifacts.parquet?rlkey=1y32rk8uzbiet9u18no760jad&dl=1) (5599 rows, 18 columns)
  - **Potential columns for visualization:**
    - **X & Y Coordinates:** `x`, `y`
    - **Point Size:** `n_tokens` (number of tokens in the abstract)
    - **Color:** Cluster labels (`cluster_05`, `cluster_08`, etc.)
    - **Label:** `title`
  - **More**:
    - [visualization notebook](https://github.com/cosmograph-org/cosmo_notebooks/blob/main/notebooks/eurovis.ipynb)
    - [data prep module eurovis.py](https://github.com/thorwhalen/imbed_data_prep/blob/main/imbed_data_prep/eurovis.py)

### Harris vs Trump Debate Dataset
- **Raw Data:** Transcript of a political debate between Kamala Harris and Donald Trump.
- **Prepared Data:** [harris_vs_trump_debate_with_extras.parquet](https://www.dropbox.com/scl/fi/tp551hfzo5xp20urs7b8x/harris_vs_trump_debate_with_extras.parquet?rlkey=4gep2vn60vv3wx5q11iq6hc3j&dl=1) (1,141 rows, 21 columns)
  - **Potential columns for visualization:**
    - **X & Y Coordinates:** `tsne__x`, `tsne__y`, `pca__x`, `pca__y`
    - **Point Size:** `certainty`
    - **Color:** `speaker_color`
    - **Label:** `text`
  - **More**:
    - [visualization notebook](https://github.com/cosmograph-org/cosmo_notebooks/blob/main/notebooks/harris_trump_debate.ipynb)

### Spotify Playlists Dataset
- **Raw Data:** Metadata on popular songs from various playlists, including holiday songs and the greatest 500 songs.
- **Prepared Data:** [holiday_songs_spotify_with_embeddings.parquet](https://www.dropbox.com/scl/fi/blchigtklrn49cp9v7aga/holiday_songs_spotify_with_embeddings.parquet?rlkey=wvr58wnj1rrx2zblsp73ufpdy&dl=1) (167 rows, 27 columns)
  - **Potential columns for visualization:**
    - **X & Y Coordinates:** `umap_x`, `umap_y`, `tsne_x`, `tsne_y`
    - **Point Size:** `popularity`
    - **Color:** `genre` (derived from playlist)
    - **Label:** `track_name`
  - **More**:
    - [visualization notebook](https://github.com/cosmograph-org/cosmo_notebooks/blob/main/notebooks/spotify_playlists.ipynb)


### Quotes Dataset
- **Raw Data:** Collection of 1,638 famous quotes.
- **Prepared Data:** [micheleriva_1638_quotes_planar_embeddings.parquet](https://www.dropbox.com/scl/fi/hgqxoi9edehwq4d17k3q7/micheleriva_1638_quotes_planar_embeddings.parquet?rlkey=wey433rcicsxkhghhlpwbskwu&dl=1) (1,638 rows, 3 columns)
  - **Potential columns for visualization:**
    - **X & Y Coordinates:** `x`, `y`
    - **Label:** `quote`
  - **More**:
    - [visualization notebook](https://github.com/cosmograph-org/cosmo_notebooks/blob/main/notebooks/quotes.ipynb)

### Prompt Injections Dataset
- **Raw Data:** Data related to prompt injection attacks and defenses.
- **Prepared Data:** [prompt_injection_w_umap_embeddings.tsv](https://www.dropbox.com/scl/fi/88lky7ogiugfkngzo8blq/prompt_injection_w_umap_embeddings.tsv?rlkey=6f1tfws5oswvzska29l1l4l2i&dl=1) (662 rows, 6 columns)
  - **Potential columns for visualization:**
    - **X & Y Coordinates:** `x`, `y`
    - **Point Size:** `size`
    - **Color:** `label`
    - **Label:** `text`
  - **More**:
    - [data prep module prompt_injections.py](https://github.com/thorwhalen/imbed_data_prep/blob/main/imbed_data_prep/prompt_injections.py)
    - [visualization notebook](https://github.com/cosmograph-org/cosmo_notebooks/blob/main/notebooks/prompt_injections.ipynb)


### LMSys Chat Conversations Dataset
- **Raw Data:** Conversations from AI chat systems.
- **Prepared Data:** [lmsys_with_planar_embeddings_pca500.parquet](https://www.dropbox.com/scl/fi/nqjg3dtaapjhjg0bloxj5/lmsys_with_planar_embeddings_pca500.parquet?rlkey=igepv3cfq9gaczztdc7bp1mb7&dl=1) (2,835,490 rows, 38 columns)
  - **Potential columns for visualization:**
    - **X & Y Coordinates:** `x_umap`, `y_umap`
    - **Point Size:** `num_of_tokens`
    - **Color:** `model`
    - **Label:** `content`
  - **Related code file:** [lmsys_ai_conversations.py](https://github.com/thorwhalen/imbed_data_prep/blob/main/imbed_data_prep/lmsys_ai_conversations.py)

### HCP Publications Dataset
- **Raw Data:** Human Connectome Project (HCP) publications and citation networks.
- **Prepared Data:** [aggregate_titles_embeddings_umap_2d_with_info.parquet](https://www.dropbox.com/scl/fi/uj14y2hre4he2iafpativ/aggregate_titles_embeddings_umap_2d_with_info.parquet?rlkey=tjey12v6cru3iq88xitytefsr&dl=1) (340,855 rows, 9 columns)
  - **Potential columns for visualization:**
    - **X & Y Coordinates:** `x`, `y`
    - **Point Size:** `n_cits` (citation count)
    - **Color:** `main_field` (research domain)
    - **Label:** `title`
  - **Related code file:** [hcp.py](https://github.com/thorwhalen/imbed_data_prep/blob/main/imbed_data_prep/hcp.py)

### GitHub Repositories Dataset
- **Raw Data:** GitHub repository metadata including stars, forks, programming languages, and repository descriptions.
- **Prepared Data:** [github_repo_for_cosmos.parquet]([https://www.dropbox.com/scl/fi/kgdvp6dmp8ppnnmjabjzl/github_repo_for_cosmos.parquet?rlkey=dma2zk9uuzsctsjfevjumbrdg&dl=1](https://www.dropbox.com/scl/fi/kgdvp6dmp8ppnnmjabjzl/github_repo_for_cosmos.parquet?rlkey=dma2zk9uuzsctsjfevjumbrdg&dl=0)) (3,065,063 rows, 28 columns)
  - **Potential columns for visualization:**
    - **X & Y Coordinates:** `x`, `y`
    - **Point Size:** `stars` (star count), `forks`
    - **Color:** `primaryLanguage`
    - **Label:** `nameWithOwner`
  - **Related code file:** [github_repos.py](https://github.com/thorwhalen/imbed_data_prep/blob/main/imbed_data_prep/github_repos.py)

## Usage Instructions
1. Load the prepared `.parquet` files into a Pandas DataFrame.
2. Use Cosmograph or another visualization tool to create scatter or force-directed plots.
3. Customize the x/y coordinates, size, color, and labels based on your analysis needs.

## Acknowledgments
- The data has been curated and prepared by [Thor Whalen](https://github.com/thorwhalen) and contributors.
- Data sources include Kaggle, Hugging Face, GitHub, and various public datasets.

For further details, please refer to the individual dataset documentation or the linked preparation scripts.



## Notebook Utilities

This section:
1. **Explains the why** (seamless Colab/local experience)
2. **Shows quick examples** (copy-pasteable)
3. **Highlights key features** (caching, auto-detection)
4. **Includes practical workflows** (typical notebook usage)
5. **Provides cache management** (helpful for power users)

`cosmodata` includes utilities to make working with data in notebooks (especially Colab) seamless.

### `ensure_installed` - Lazy Dependency Management

Install packages only when needed, with smart local/Colab detection.
Note: Most of the time you can just do `%pip install -q ...packages` in your notebook,
but if you want to ask permission to the user first (which I like doing), 
or need to ensure installation from python itself, this could help. 

```python
from cosmodata import ensure_installed

# Simple: space-separated package names
ensure_installed('graze tabled pandas')

# With version requirements
ensure_installed('graze>=0.1.0 tabled pandas<2.0')

# Handle import/pip name mismatches
ensure_installed('PIL cv2', pip_names={'PIL': 'Pillow', 'cv2': 'opencv-python'})
```

**Behavior:**
- **In Colab**: Auto-installs missing packages silently
- **Locally**: Shows what will be installed and asks for confirmation (default: Yes)
- **Smart**: Only installs if package is missing or version doesn't satisfy requirements

### `acquire_data` - Unified Data Loading with Caching

Load data from URLs or files with automatic caching. Works seamlessly in Colab (Google Drive) and locally.

```python
from cosmodata import acquire_data

# Load CSV from URL (cached automatically)
df = acquire_data('https://example.com/data.csv')

# Custom getter for APIs
data = acquire_data(
    'https://api.example.com/endpoint',
    getter=lambda url: requests.get(url).json(),
    cache_key='api_data'
)

# Force refresh cached data
df = acquire_data(url, refresh=True)

# Custom cache location
df = acquire_data(url, cache_dir='/path/to/cache')
```

**Features:**
- **Auto-caching**: 
  - Colab: Saves to Google Drive (`MyDrive/.colab_cache`) for persistence across sessions
  - Local: Saves to `~/.local/share/cosmodata/datasets`
- **Smart getters**: Auto-detects appropriate loader (graze → tabled → requests)
- **Refresh support**: Bypass cache with `refresh=True`
- **Format support**: Handles CSV, JSON, Excel, Parquet, etc. (via `tabled`)

**Typical notebook workflow:**

```python
# Cell 1: Setup
!pip install cosmodata
from cosmodata import ensure_installed, acquire_data

ensure_installed('graze tabled pandas')

# Cell 2: Load data (fast on subsequent runs)
df = acquire_data('https://example.com/large_dataset.csv', cache_key='my_dataset')

# Cell 3: Your analysis
df.head()
```

**Cache management:**

```python
# See where data is cached
import os
from pathlib import Path

# In Colab
cache_dir = Path('/content/drive/MyDrive/.colab_cache')

# Locally
cache_dir = Path('~/.local/share/cosmodata/datasets').expanduser()

# List cached files
list(cache_dir.glob('*.pkl'))

# Clear specific cache
os.remove(cache_dir / 'my_dataset.pkl')
```

---

**Pro tip**: Combine both utilities for the smoothest notebook experience:

```python
from cosmodata import ensure_installed, acquire_data

# One-time setup
ensure_installed('graze tabled requests')

# Now your data loading "just works" with caching
df1 = acquire_data('https://example.com/data.csv')
df2 = acquire_data('local_file.parquet')
api_data = acquire_data(
    'https://api.example.com/data',
    getter=lambda u: requests.get(u).json()
)
```
