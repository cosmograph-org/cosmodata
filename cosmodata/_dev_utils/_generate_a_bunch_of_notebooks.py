"""Generate notebooks for all datasets.

This script creates Jupyter notebooks for various datasets by parsing
markdown descriptions and generating standardized notebook templates.
"""

from pathlib import Path
from cosmodata.notebook_gen import NotebookParams, create_notebook


def _resolve_output_dir(output_dir=None):
    """Return a Path to an existing directory, prompting the user if needed."""
    candidate = output_dir
    while candidate is None or not candidate:
        candidate = input("Enter output directory for generated notebooks: ").strip()
    path = Path(candidate).expanduser()
    while not path.is_dir():
        candidate = input(
            f"Directory '{path}' does not exist. Please enter a valid directory: "
        ).strip()
        if not candidate:
            continue
        path = Path(candidate).expanduser()
    return path


def generate_all_notebooks(datasets: dict = None, output_dir=None):
    """Generate notebooks for all datasets."""
    if datasets is None:
        from cosmodata.base import datas

        datasets = datas

    resolved_output_dir = _resolve_output_dir(output_dir)
    for dataset_config in datasets:
        output_filename = dataset_config["output_filename"]
        output_path = resolved_output_dir / output_filename
        params_kwargs = {
            k: v for k, v in dataset_config.items() if k != "output_filename"
        }
        params = NotebookParams(**params_kwargs)

        print(f"Generating {output_filename}...")
        create_notebook(params, output_path=str(output_path))
        print(f"  ✓ Saved to {output_path}")

    print(f"\n✅ Successfully generated {len(datasets)} notebooks!")


def generate_individual_notebooks(output_dir=None):
    """Alternative approach: Generate notebooks one by one with explicit calls."""
    resolved_output_dir = _resolve_output_dir(output_dir)

    # GitHub Repositories
    create_notebook(
        NotebookParams(
            src="https://www.dropbox.com/scl/fi/kgdvp6dmp8ppnnmjabjzl/github_repo_for_cosmos.parquet?rlkey=dma2zk9uuzsctsjfevjumbrdg&dl=1",
            target_filename="github_repo_for_cosmos.parquet",
            dataset_name="GitHub Repositories Dataset",
            dataset_description="GitHub repository metadata including stars, forks, programming languages, and repository descriptions.",
            ext=".parquet",
            viz_columns_info="""**Potential columns for visualization:**
    - **X & Y Coordinates:** `x`, `y`
    - **Point Size:** `stars` (star count), `forks`
    - **Color:** `primaryLanguage`
    - **Label:** `nameWithOwner`""",
            related_code="[github_repos.py](https://github.com/thorwhalen/imbed_data_prep/blob/main/imbed_data_prep/github_repos.py)",
        ),
        output_path=str(resolved_output_dir / "github_repositories.ipynb"),
    )

    # HCP Publications
    create_notebook(
        NotebookParams(
            src="https://www.dropbox.com/scl/fi/uj14y2hre4he2iafpativ/aggregate_titles_embeddings_umap_2d_with_info.parquet?rlkey=tjey12v6cru3iq88xitytefsr&dl=1",
            target_filename="aggregate_titles_embeddings_umap_2d_with_info.parquet",
            dataset_name="HCP Publications Dataset",
            dataset_description="Human Connectome Project (HCP) publications and citation networks.",
            ext=".parquet",
            viz_columns_info="""**Potential columns for visualization:**
    - **X & Y Coordinates:** `x`, `y`
    - **Point Size:** `n_cits` (citation count)
    - **Color:** `main_field` (research domain)
    - **Label:** `title`""",
            related_code="[hcp.py](https://github.com/thorwhalen/imbed_data_prep/blob/main/imbed_data_prep/hcp.py)",
        ),
        output_path=str(resolved_output_dir / "hcp_publications.ipynb"),
    )

    # Harris vs Trump Debate
    create_notebook(
        NotebookParams(
            src="https://www.dropbox.com/scl/fi/tp551hfzo5xp20urs7b8x/harris_vs_trump_debate_with_extras.parquet?rlkey=4gep2vn60vv3wx5q11iq6hc3j&dl=1",
            target_filename="harris_vs_trump_debate_with_extras.parquet",
            dataset_name="Harris vs Trump Debate Dataset",
            dataset_description="Transcript of a political debate between Kamala Harris and Donald Trump.",
            ext=".parquet",
            viz_columns_info="""**Potential columns for visualization:**
    - **X & Y Coordinates:** `tsne__x`, `tsne__y`, `pca__x`, `pca__y`
    - **Point Size:** `certainty`
    - **Color:** `speaker_color`
    - **Label:** `text`""",
        ),
        output_path=str(resolved_output_dir / "harris_trump_debate.ipynb"),
    )

    # Spotify Playlists
    create_notebook(
        NotebookParams(
            src="https://www.dropbox.com/scl/fi/blchigtklrn49cp9v7aga/holiday_songs_spotify_with_embeddings.parquet?rlkey=wvr58wnj1rrx2zblsp73ufpdy&dl=1",
            target_filename="holiday_songs_spotify_with_embeddings.parquet",
            dataset_name="Spotify Playlists Dataset",
            dataset_description="Metadata on popular songs from various playlists, including holiday songs and the greatest 500 songs.",
            ext=".parquet",
            viz_columns_info="""**Potential columns for visualization:**
    - **X & Y Coordinates:** `umap_x`, `umap_y`, `tsne_x`, `tsne_y`
    - **Point Size:** `popularity`
    - **Color:** `genre` (derived from playlist)
    - **Label:** `track_name`""",
        ),
        output_path=str(resolved_output_dir / "spotify_playlists.ipynb"),
    )

    # LMSys Chat Conversations
    create_notebook(
        NotebookParams(
            src="https://www.dropbox.com/scl/fi/nqjg3dtaapjhjg0bloxj5/lmsys_with_planar_embeddings_pca500.parquet?rlkey=igepv3cfq9gaczztdc7bp1mb7&dl=1",
            target_filename="lmsys_with_planar_embeddings_pca500.parquet",
            dataset_name="LMSys Chat Conversations Dataset",
            dataset_description="Conversations from AI chat systems.",
            ext=".parquet",
            viz_columns_info="""**Potential columns for visualization:**
    - **X & Y Coordinates:** `x_umap`, `y_umap`
    - **Point Size:** `num_of_tokens`
    - **Color:** `model`
    - **Label:** `content`""",
            related_code="[lmsys_ai_conversations.py](https://github.com/thorwhalen/imbed_data_prep/blob/main/imbed_data_prep/lmsys_ai_conversations.py)",
        ),
        output_path=str(resolved_output_dir / "lmsys_chat_conversations.ipynb"),
    )

    # Prompt Injections
    create_notebook(
        NotebookParams(
            src="https://www.dropbox.com/scl/fi/88lky7ogiugfkngzo8blq/prompt_injection_w_umap_embeddings.tsv?rlkey=6f1tfws5oswvzska29l1l4l2i&dl=1",
            target_filename="prompt_injection_w_umap_embeddings.tsv",
            dataset_name="Prompt Injections Dataset",
            dataset_description="Data related to prompt injection attacks and defenses.",
            ext=".tsv",
            viz_columns_info="""**Potential columns for visualization:**
    - **X & Y Coordinates:** `x`, `y`
    - **Point Size:** `size`
    - **Color:** `label`
    - **Label:** `text`""",
            related_code="[prompt_injections.py](https://github.com/thorwhalen/imbed_data_prep/blob/main/imbed_data_prep/prompt_injections.py)",
        ),
        output_path=str(resolved_output_dir / "prompt_injections.ipynb"),
    )

    # Quotes
    create_notebook(
        NotebookParams(
            src="https://www.dropbox.com/scl/fi/hgqxoi9edehwq4d17k3q7/micheleriva_1638_quotes_planar_embeddings.parquet?rlkey=wey433rcicsxkhghhlpwbskwu&dl=1",
            target_filename="micheleriva_1638_quotes_planar_embeddings.parquet",
            dataset_name="Quotes Dataset",
            dataset_description="Collection of 1,638 famous quotes.",
            ext=".parquet",
            viz_columns_info="""**Potential columns for visualization:**
    - **X & Y Coordinates:** `x`, `y`
    - **Label:** `quote`""",
        ),
        output_path=str(resolved_output_dir / "quotes.ipynb"),
    )

    print("\n✅ Successfully generated all notebooks!")


if __name__ == "__main__":
    # Use the loop-based approach (recommended)
    generate_all_notebooks()

    # Or use individual function calls (alternative)
    # generate_individual_notebooks()
