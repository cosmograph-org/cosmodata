"""Generate Jupyter notebooks from template parameters.

This module provides functionality to create standardized Jupyter notebooks for data
analysis and visualization projects. It uses a template-based approach with
customizable parameters.

Installation:
    pip install notebook_gen

Usage:
    >>> from notebook_gen import NotebookParams, create_notebook
    >>> params = NotebookParams(
    ...     src='https://example.com/data.parquet',
    ...     target_filename='my_data.parquet',
    ...     dataset_name='My Dataset',
    ...     dataset_description='Description of the dataset'
    ... )
    >>> notebook_dict = create_notebook(params, output_path='output.ipynb')
"""

from dataclasses import dataclass, field
from typing import Optional, Any
import json


@dataclass
class NotebookParams:
    """Parameters for generating a Jupyter notebook.

    Examples:
        >>> params = NotebookParams(
        ...     src='https://example.com/data.csv',
        ...     target_filename='data.csv',
        ...     dataset_name='Test Dataset',
        ...     dataset_description='A test dataset'
        ... )
        >>> params.src
        'https://example.com/data.csv'
    """

    # Required parameters
    src: str
    target_filename: str
    dataset_name: str
    dataset_description: str

    # Optional parameters with defaults
    ext: Optional[str] = None
    install: str = "cosmograph tabled cosmodata"
    installs_not_to_import: list[str] = field(default_factory=lambda: ["cosmograph"])
    imports: str = field(
        default_factory=lambda: """from functools import partial 
from cosmograph import cosmo"""
    )
    viz_columns_info: Optional[str] = None
    related_code: Optional[str] = None
    peep_mode: str = "short"
    peep_exclude_cols: list[str] = field(default_factory=list)


def create_notebook(
    params: NotebookParams, *, output_path: Optional[str] = None, n_viz_cells: int = 5
) -> dict[str, Any]:
    """Generate a Jupyter notebook from parameters.

    Args:
        params: NotebookParams instance with all configuration
        output_path: Optional path to save the notebook JSON
        n_viz_cells: Number of empty visualization cells to create

    Returns:
        Dictionary representing the notebook JSON structure

    Examples:
        >>> params = NotebookParams(
        ...     src='https://example.com/data.csv',
        ...     target_filename='data.csv',
        ...     dataset_name='Test',
        ...     dataset_description='Test data'
        ... )
        >>> nb = create_notebook(params)
        >>> nb['nbformat']
        4
    """
    cells = [
        _create_dataset_description_cell(params),
        _create_markdown_cell("## Get data"),
        _create_markdown_cell("### Data parameters"),
        _create_data_params_cell(params),
        _create_markdown_cell("### Install and import"),
        _create_install_import_cell(params),
        _create_markdown_cell("### Load data"),
        _create_load_data_cell(params),
        _create_markdown_cell("## Peep at the data"),
        _create_peep_data_cell(params),
        _create_markdown_cell("## Visualize data"),
    ]

    # Add empty visualization cells
    cells.extend(_create_code_cell("") for _ in range(n_viz_cells))

    notebook = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "codemirror_mode": {"name": "ipython", "version": 3},
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.12.0",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }

    if output_path:
        _save_notebook(notebook, output_path)

    return notebook


def _create_markdown_cell(content: str) -> dict[str, Any]:
    """Create a markdown cell.

    Examples:
        >>> cell = _create_markdown_cell("# Title")
        >>> cell['cell_type']
        'markdown'
    """
    return {
        "cell_type": "markdown",
        "id": _generate_cell_id(),
        "metadata": {},
        "source": content,
    }


def _create_code_cell(
    code: str, *, execution_count: Optional[int] = None
) -> dict[str, Any]:
    """Create a code cell.

    Examples:
        >>> cell = _create_code_cell("print('hello')")
        >>> cell['cell_type']
        'code'
    """
    return {
        "cell_type": "code",
        "execution_count": execution_count,
        "id": _generate_cell_id(),
        "metadata": {},
        "outputs": [],
        "source": code,
    }


def _create_dataset_description_cell(params: NotebookParams) -> dict[str, Any]:
    """Create the dataset description markdown cell."""
    content_parts = [f"### {params.dataset_name}"]

    if params.dataset_description:
        content_parts.append(f"- **Description:** {params.dataset_description}")

    if params.src:
        # Extract filename from URL if available
        filename = params.target_filename or params.src.split('/')[-1].split('?')[0]
        content_parts.append(f"- **Data Source:** [{filename}]({params.src})")

    if params.viz_columns_info:
        content_parts.append(f"  - {params.viz_columns_info}")

    if params.related_code:
        content_parts.append(f"  - **Related code file:** {params.related_code}")

    return _create_markdown_cell("\n".join(content_parts))


def _create_data_params_cell(params: NotebookParams) -> dict[str, Any]:
    """Create the data parameters code cell."""
    lines = []

    if params.ext:
        lines.append(f"ext = {repr(params.ext)}")

    lines.append(f"src = {repr(params.src)}")
    lines.append(f"target_filename = {repr(params.target_filename)}")

    return _create_code_cell("\n".join(lines))


def _create_install_import_cell(params: NotebookParams) -> dict[str, Any]:
    """Create the install and import code cell."""
    lines = ["import os", "if not os.getenv('IN_COSMO_DEV_ENV'):"]

    if params.install:
        lines.append(f"    %pip install -q {params.install}")

    lines.append("")

    # Import packages that were installed
    installed_packages = params.install.split()
    for pkg in installed_packages:
        if pkg not in params.installs_not_to_import:
            lines.append(f"import {pkg}")

    if params.imports:
        lines.append("")
        lines.append(params.imports)

    return _create_code_cell("\n".join(lines))


def _create_load_data_cell(params: NotebookParams) -> dict[str, Any]:
    """Create the load data code cell."""
    code = """if ext:
    getter = partial(tabled.get_table, ext=ext)
else:
    getter = tabled.get_table
# acquire_data takes care of caching locally too, so next time access will be faster
# (If you want a fresh copy, you can delete the local cache file manually.)
data = cosmodata.acquire_data(src, target_filename, getter=getter)"""
    return _create_code_cell(code)


def _create_peep_data_cell(params: NotebookParams) -> dict[str, Any]:
    """Create the peep at data code cell."""
    exclude_repr = repr(params.peep_exclude_cols) if params.peep_exclude_cols else "[]"

    code = f"""mode = {repr(params.peep_mode)}  #Literal['short', 'sample', 'stats'] = 'short',
exclude_cols = {exclude_repr}
cosmodata.print_dataframe_info(data, exclude_cols, mode=mode)"""
    return _create_code_cell(code)


def _save_notebook(notebook: dict[str, Any], output_path: str) -> None:
    """Save notebook dictionary to a JSON file."""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(notebook, f, indent=1, ensure_ascii=False)


def _generate_cell_id() -> str:
    """Generate a unique cell ID."""
    import uuid

    return uuid.uuid4().hex[:8]


# Convenience function for markdown-based input
def create_notebook_from_markdown(
    markdown_info: str,
    src: str,
    target_filename: str,
    *,
    ext: Optional[str] = None,
    output_path: Optional[str] = None,
    **kwargs,
) -> dict[str, Any]:
    """Create a notebook from markdown-formatted dataset information.

    This function parses markdown text to extract dataset information and creates
    a notebook. Use this when you have markdown-formatted metadata.

    Args:
        markdown_info: Markdown text describing the dataset
        src: URL or path to the data source
        target_filename: Name for the cached/downloaded file
        ext: Optional file extension
        output_path: Optional path to save the notebook
        **kwargs: Additional parameters passed to NotebookParams

    Returns:
        Dictionary representing the notebook JSON structure
    """
    # Extract dataset name (first header)
    lines = markdown_info.strip().split('\n')
    dataset_name = lines[0].replace('#', '').strip()

    # Use the rest as description
    dataset_description = '\n'.join(lines[1:]).strip()

    params = NotebookParams(
        src=src,
        target_filename=target_filename,
        dataset_name=dataset_name,
        dataset_description=dataset_description,
        ext=ext,
        **kwargs,
    )

    return create_notebook(params, output_path=output_path)
