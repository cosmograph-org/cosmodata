# cosmodata — agent guide

A Python **portal to data sources**: a registry/catalog of curated, Cosmograph-ready datasets
(mostly Parquet with x/y embedding columns), with cached acquisition and notebook generation. Also
home to an **LLM mapping advisor** for column→visual-parameter suggestions.

## Two roles

### 1) Dataset catalog / acquisition
```python
from cosmodata import acquire_data            # cached download/load of any URL/file → DataFrame
from cosmodata.base import metas, datas       # dol stores over the catalog
list(metas); df = datas['quotes']             # slugs → loaded, cached, ready DataFrames
```
- `cosmodata/meta/*.json` — the catalog (each: `src`, `ext`, `viz_columns_info` recommended mappings).
- `cosmodata/base.py` — `acquire_data`, `metas`, `datas`. `cosmodata/util.py` — link-tables, caching.
- `cosmodata/notebook_gen.py` — generate standardized analysis/viz notebooks per dataset.
- `README.md` — human catalog with recommended x/y/size/color/label mappings.

### 2) Mapping advisor (dev util)
`cosmodata/_dev_utils/_cosmo_params.py`:
- `suggest_cosmo_parameters(df, n_suggestions=...)` — LLM suggests column→visual mappings.
- `cosmo_dataset_viz_params_output_schema` — output JSON Schema (points2d|graph|timeline|matrix).
- `cosmo_param_suggestion_prompt_template`, `cosmo_params_description` — the prompt + param reference.
- `insert_visualizations_in_notebook(...)` — materialize suggestions as runnable notebook cells.

**Caveat:** the hardcoded `cosmo_params_description` defaults drift from the canonical
`params_ssot.json` (in `py_cosmograph`) — treat the SSOT as authoritative.

## Caveats
- Heavy raw→prepared transforms live in the sibling repo `imbed_data_prep` (outside this repo).
- Prepared data is hosted at external (Dropbox) URLs; availability is an external dependency.

## Broader context
For acquisition and mapping in the full data-prep journey, see the `cosmo-data-acquire` and
`cosmo-data-mapping` skills in the parent `c/` workspace (`c/.claude/skills/`).
