"""Dev utils"""

from functools import partial
from collections.abc import Iterable
from pathlib import Path
import json

import nbformat
import pandas as pd
from nbformat import v4 as nbf

from cosmodata.util import print_dataframe_info

dataframe_info_string = partial(print_dataframe_info, mode='sample', egress=None)


def cosmo_parameter_description_string():
    """Generate parameter description string for cosmo function.

    cosmograph.base.cosmo_base_params_doc_str is not ordered like Sig(cosmo).
    This is the only reason the present function exists.
    """
    # TODO: Order cosmograph.base.cosmo_base_params_doc_str correctly.
    from cosmograph.util import _params_ssot, params_to_docstring, cosmograph_base_docs
    from cosmograph import cosmo
    from i2 import Sig

    # cosmograph_base_docs(Sig(cosmo).names)
    params_ssot = {x['name']: x for x in _params_ssot()}
    params_ssot = {
        k: params_ssot[k]
        for k in Sig(cosmo).names
        if k in params_ssot and k not in {'points', 'links'}  # because these are data
    }
    params_ssot = list(params_ssot.values())

    normal_docstring = params_to_docstring(params_ssot)

    additional_docs = """
    Note that all parameters that end with `_by` accept either a column name (str) 
    referring to a column in the respective DataFrame.
    Some explanations of parameters are not given (but should be obvious from context).

    """

    return additional_docs + normal_docstring


def _save_parameter_description_to_file():
    filepath = '/Users/thorwhalen/Dropbox/_odata/ai_contexts/projects/cosmo_backend/cosmo_parameter_descriptions.md'
    desc_str = cosmo_parameter_description_string()
    with open(filepath, 'w') as f:
        f.write(desc_str)


cosmo_dataset_viz_params_output_schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://example.com/schemas/cosmo-visualizations-only.json",
    "title": "Cosmograph Visualizations (Agent Output)",
    "type": "object",
    "properties": {
        "visualizations": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "properties": {
                    "slug": {"type": "string", "description": "URL-safe identifier"},
                    "title": {
                        "type": "string",
                        "description": "Short visualization title",
                    },
                    "explanation_md": {
                        "type": "string",
                        "description": "Markdown explanation (no code fences required)",
                    },
                    "visualization_type": {
                        "type": "string",
                        "enum": ["points2d", "graph", "timeline", "matrix", "other"],
                        "default": "points2d",
                    },
                    "mappings": {
                        "type": "object",
                        "description": "Explicit data-to-visual mappings using *_by fields.",
                        "properties": {
                            "point_x_by": {
                                "type": "string",
                                "description": "Numeric column for X coordinate",
                            },
                            "point_y_by": {
                                "type": "string",
                                "description": "Numeric column for Y coordinate",
                            },
                            "point_size_by": {
                                "type": "string",
                                "description": "Column mapping to point size",
                            },
                            "point_color_by": {
                                "type": "string",
                                "description": "Column mapping to point color",
                            },
                            "point_label_by": {
                                "type": "string",
                                "description": "Column mapping to point label text",
                            },
                            "point_id_by": {
                                "type": "string",
                                "description": "Stable unique ID for each point",
                            },
                            "point_index_by": {
                                "type": "string",
                                "description": "Integer index for each point",
                            },
                            "point_label_weight_by": {
                                "type": "string",
                                "description": "Label importance weighting",
                            },
                            "point_cluster_by": {
                                "type": "string",
                                "description": "Cluster/category assignment",
                            },
                            "point_cluster_strength_by": {
                                "type": "string",
                                "description": "Cluster strength value",
                            },
                            "point_timeline_by": {
                                "type": "string",
                                "description": "Date/number column enabling timeline",
                            },
                            "link_source_by": {
                                "type": "string",
                                "description": "Link source IDs (or labels)",
                            },
                            "link_source_index_by": {
                                "type": "string",
                                "description": "Numeric source indices",
                            },
                            "link_target_by": {
                                "type": "string",
                                "description": "Link target IDs (or labels)",
                            },
                            "link_target_index_by": {
                                "type": "string",
                                "description": "Numeric target indices",
                            },
                            "link_color_by": {
                                "type": "string",
                                "description": "Link color mapping",
                            },
                            "link_width_by": {
                                "type": "string",
                                "description": "Link width mapping",
                            },
                            "link_arrow_by": {
                                "type": "string",
                                "description": "Arrow visibility/direction mapping",
                            },
                            "link_strength_by": {
                                "type": "string",
                                "description": "Link spring strength mapping",
                            },
                        },
                        "additionalProperties": False,
                    },
                    "cosmo_params": {
                        "type": "object",
                        "description": "Optional non-* _by Cosmograph parameters.",
                        "properties": {
                            "point_color_palette": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                            "point_color_by_map": {
                                "type": "array",
                                "items": {
                                    "type": "array",
                                    "items": {
                                        "oneOf": [
                                            {"type": "string"},
                                            {
                                                "type": "array",
                                                "items": {"type": "number"},
                                                "minItems": 3,
                                                "maxItems": 4,
                                            },
                                        ]
                                    },
                                    "minItems": 2,
                                    "maxItems": 2,
                                },
                            },
                            "point_color_strategy": {"type": "string"},
                            "point_color": {
                                "oneOf": [
                                    {"type": "string"},
                                    {"type": "array", "items": {"type": "number"}},
                                ]
                            },
                            "point_greyout_opacity": {"type": "number"},
                            "point_size": {"type": "number"},
                            "point_size_scale": {"type": "number"},
                            "point_sampling_distance": {"type": "integer"},
                            "point_size_range": {
                                "type": "array",
                                "items": {"type": "number"},
                                "minItems": 2,
                                "maxItems": 2,
                            },
                            "point_include_columns": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                            "link_color": {
                                "oneOf": [
                                    {"type": "string"},
                                    {"type": "array", "items": {"type": "number"}},
                                ]
                            },
                            "link_greyout_opacity": {"type": "number"},
                            "link_width": {"type": "number"},
                            "link_width_scale": {"type": "number"},
                            "link_arrows": {"type": "boolean"},
                            "link_arrows_size_scale": {"type": "number"},
                            "link_visibility_distance_range": {
                                "type": "array",
                                "items": {"type": "number"},
                                "minItems": 2,
                                "maxItems": 2,
                            },
                            "link_visibility_min_transparency": {"type": "number"},
                            "link_strength_range": {
                                "type": "array",
                                "items": {"type": "number"},
                                "minItems": 2,
                                "maxItems": 2,
                            },
                            "link_include_columns": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                            "disable_simulation": {"type": "boolean"},
                            "simulation_decay": {"type": "number"},
                            "simulation_gravity": {"type": "number"},
                            "simulation_center": {"type": "number"},
                            "simulation_repulsion": {"type": "number"},
                            "simulation_repulsion_theta": {"type": "number"},
                            "simulation_repulsion_quadtree_levels": {"type": "number"},
                            "simulation_link_spring": {"type": "number"},
                            "simulation_link_distance": {"type": "number"},
                            "simulation_link_dist_random_variation_range": {
                                "type": "array",
                                "items": {},
                                "minItems": 2,
                                "maxItems": 2,
                            },
                            "simulation_repulsion_from_mouse": {"type": "number"},
                            "simulation_friction": {"type": "number"},
                            "simulation_cluster": {"type": "number"},
                            "background_color": {
                                "oneOf": [
                                    {"type": "string"},
                                    {"type": "array", "items": {"type": "number"}},
                                ]
                            },
                            "space_size": {"type": "integer"},
                            "hovered_point_cursor": {"type": "string"},
                            "render_hovered_point_ring": {"type": "boolean"},
                            "hovered_point_ring_color": {
                                "oneOf": [
                                    {"type": "string"},
                                    {"type": "array", "items": {"type": "number"}},
                                ]
                            },
                            "focused_point_ring_color": {
                                "oneOf": [
                                    {"type": "string"},
                                    {"type": "array", "items": {"type": "number"}},
                                ]
                            },
                            "focused_point_index": {"type": "integer"},
                            "render_links": {"type": "boolean"},
                            "curved_links": {"type": "boolean"},
                            "curved_link_segments": {"type": "integer"},
                            "curved_link_weight": {"type": "number"},
                            "curved_link_control_point_distance": {"type": "number"},
                            "use_quadtree": {"type": "boolean"},
                            "show_FPS_monitor": {"type": "boolean"},
                            "pixel_ratio": {"type": "number"},
                            "scale_points_on_zoom": {"type": "boolean"},
                            "initial_zoom_level": {"type": "number"},
                            "disable_zoom": {"type": "boolean"},
                            "enable_drag": {"type": "boolean"},
                            "fit_view_on_init": {"type": "boolean"},
                            "fit_view_delay": {"type": "number"},
                            "fit_view_padding": {"type": "number"},
                            "fit_view_duration": {"type": "number"},
                            "fit_view_by_points_in_rect": {
                                "type": "array",
                                "items": {"type": "array", "items": {"type": "number"}},
                            },
                            "random_seed": {
                                "oneOf": [{"type": "integer"}, {"type": "string"}]
                            },
                            "show_labels": {"type": "boolean"},
                            "show_dynamic_labels": {"type": "boolean"},
                            "show_labels_for": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                            "show_top_labels": {"type": "boolean"},
                            "show_top_labels_limit": {"type": "integer"},
                            "show_top_labels_by": {"type": "string"},
                            "static_label_weight": {"type": "number"},
                            "dynamic_label_weight": {"type": "number"},
                            "label_margin": {"type": "number"},
                            "show_hovered_point_label": {"type": "boolean"},
                            "disable_point_size_legend": {"type": "boolean"},
                            "disable_link_width_legend": {"type": "boolean"},
                            "disable_point_color_legend": {"type": "boolean"},
                            "disable_link_color_legend": {"type": "boolean"},
                            "clicked_point_index": {"type": "integer"},
                            "clicked_point_id": {"type": "string"},
                            "selected_point_indices": {
                                "type": "array",
                                "items": {"type": "integer"},
                            },
                            "selected_point_ids": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                            "changePoints": {
                                "type": "string",
                                "description": "Callback identifier/name",
                            },
                            "changeLinks": {
                                "type": "string",
                                "description": "Callback identifier/name",
                            },
                        },
                        "additionalProperties": True,
                    },
                    "include_columns": {"type": "array", "items": {"type": "string"}},
                    "insight_bullets": {"type": "array", "items": {"type": "string"}},
                    "assumptions": {"type": "array", "items": {"type": "string"}},
                    "cosmo_call": {
                        "type": "string",
                        "description": "A single raw Python function call to cosmo(...). No fenced code.",
                    },
                },
                "required": ["title", "explanation_md", "mappings", "cosmo_call"],
                "allOf": [
                    {
                        "if": {
                            "properties": {"visualization_type": {"const": "graph"}},
                            "required": ["visualization_type"],
                        },
                        "then": {
                            "properties": {
                                "mappings": {
                                    "allOf": [
                                        {
                                            "required": [
                                                "link_source_by",
                                                "link_target_by",
                                            ]
                                        }
                                    ]
                                }
                            }
                        },
                    },
                    {
                        "if": {
                            "properties": {
                                "visualization_type": {
                                    "enum": ["points2d", "timeline", "matrix", "other"]
                                }
                            },
                            "required": ["visualization_type"],
                        },
                        "then": {
                            "properties": {
                                "mappings": {
                                    "anyOf": [
                                        {"required": ["point_x_by", "point_y_by"]},
                                        {"required": ["point_x_by"]},
                                        {"required": ["point_y_by"]},
                                    ]
                                }
                            }
                        },
                    },
                ],
            },
        }
    },
    "required": ["visualizations"],
    "additionalProperties": False,
}

cosmo_params_description = """
All `*_by` parameters accept column names (str) from the respective DataFrame.

**Point Parameters:**
point_x_by, point_y_by, point_size_by, point_color_by, point_label_by, point_id_by, point_index_by: str - Column mappings for point attributes.
point_color: str|list[float]="#b3b3b3" - Point color.
point_size: float=4 - Base point size.
point_size_scale: float=1 - Point size multiplier.
point_size_range: list[float] - Min/max size bounds.
point_color_palette: list[str] - Colors for palette/interpolation strategies.
point_color_by_map: list[list[str|list[float]]] - Value-to-color mapping.
point_color_strategy: str - How to apply colors from point_color_by ('palette'|'interpolatePalette'|'degree'|'map').
point_greyout_opacity: float=0.1 - Opacity of unselected points.
point_cluster_by, point_cluster_strength_by, point_label_weight_by, point_timeline_by: str - Advanced column mappings.
point_include_columns: list[str] - Additional columns to include in point data.

**Link Parameters:**
link_source_by, link_target_by, link_source_index_by, link_target_index_by: str - Link endpoint mappings.
link_color_by, link_width_by, link_arrow_by, link_strength_by: str - Link attribute column mappings.
link_color: str|list[float]="#666666", link_width: float=1 - Base link appearance.
link_width_scale: float=1, link_arrows_size_scale: float=1 - Link attribute multipliers.
link_greyout_opacity: float=0.1 - Opacity of unselected links.
link_arrows: bool - Show directional arrows.
link_strength_range: list[float] - Min/max link force bounds.
link_include_columns: list[str] - Additional columns to include in link data.

**Simulation:**
disable_simulation: bool=False - Skip force simulation.
simulation_decay: float=1000 - Simulation cooldown speed.
simulation_repulsion: float=0.1 - Point-to-point repulsion force.
simulation_link_spring: float=1, simulation_link_distance: float=2 - Link force parameters.
simulation_gravity: float=0, simulation_center: float=0 - Centering forces.
simulation_friction: float=0.85 - Movement dampening.

**Display:**
background_color: str|list[float]="#222222", space_size: int=4096 - Canvas settings.
render_links: bool=True - Show/hide links.
curved_links: bool=False - Use curved instead of straight links.
scale_points_on_zoom: bool=True - Scale points with zoom level.

**View/Zoom:**
initial_zoom_level: float=3, disable_zoom: bool=False - Zoom settings.
fit_view_on_init: bool=True - Auto-fit view on load.

**Labels:**
show_labels, show_dynamic_labels, show_hovered_point_label: bool - Label visibility options.
show_top_labels: bool, show_top_labels_limit: int, show_top_labels_by: str - Show labels for top-ranked points.
show_labels_for: list[str] - Specific point IDs to label.

**Interaction/Selection:**
focused_point_index: int, clicked_point_index: int, clicked_point_id: str - Point focus/click state.
selected_point_indices: list[int], selected_point_ids: list[str] - Multi-select state.

**Callbacks:**
changePoints, changeLinks: Callable - Callbacks for data updates.
"""

cosmo_param_suggestion_prompt_template = r"""
You are an expert data scientist specializing in data visualization, especially using the cosmograph tool, which is meant to visualize points data (like scatter plots) as well as link data (points, with links between them). 

Your main goal is to help users use cosmo tool, namely to help them map data 
columns to cosmograph (visual) parameters/arguments

The user will share, below, some data information with you (like the first row of a d
dataframe, perhaps it's dimensions too, or a sample of rows) and you should figure out one or several ways you can map the columns to visual properties to make beautiful informative graphs. 

As far as the cosmo function is a function with the following signature:

```py
def cosmo(
    data=None,
    *,
    points: object = None,
    links: object = None,

    ... a bunch of other visual mapping parameters

```

The data is a pandas dataframe (that will be used either as points, or as links, 
according to the data_resolution logic (which by default priortizes points. The user can also explicitly state whether the data is "points" data or "links" data (for visualizing graphs, the user will need both usually). Again, the data parameter is just a convenience, it is immediately assigned to points or to links. 
Then there is a few specialized functions (not needed most of the time):

This is what all the other parameters control. 
You can see the list of parameters here:

{cosmo_params_description}

Note, again, that all parameters that end with `_by` accept either a column name (str) 
referring to a column in the respective DataFrame.
The main ones are:
point_x_by and point_y_by to specify what (numerical) columns (names) to take for the 
coordinates of the point (not necessary in linked data) point_size_by to determine 
the size, point_color_by to determine the color. 
You should favor columns named `x` and `y`, or ending with `_x` and `_y` for the coordinates
(the point_x_by and point_y_by parameters). 
You should favor categorical columns for point_color_by and numerical columns for point_size_by.

There are essentially two types of graphs:
* points: You necessarily need to specify a point_x_by and point_y_by here. This could 
be any numerical columns (for example, if you want to compare "height" (x) with "weight" (y)), 
but very often the data will also hint at some ways you could map the coordinates, since they'll start or finish with "x" or "y". 
Bear in mind that often these x and y are computed from multidimensional "embeddings" or "feature vectors", 
which have been "planarized" to fit on a 2D screen.
* links: For this you'll necessarily need a to specify links and specify the source and target of these links 
(via link_source_by/link_target_by or link_source_index_by/link_target_index_by)

Your response should be a json with the provided schema. 

Below is a description of the data and/or points and/or links.
If the description is empty, it means there was no such input.
This should indicate how you should categorize the type of graph.

Give me {{n_suggestions}} different suggestions for visualizations I can make with this data,

Description of the data:
{{data_description}}

Description of the points:
{{points_description}}

Description of the links:
{{links_description}}

""".format(
    cosmo_params_description=cosmo_params_description
)


def suggest_cosmo_parameters(
    data,
    extra_instructions: str = '',
    *,
    n_suggestions : int = 2,
    points=None,
    links=None,
    info_extractor=dataframe_info_string,
    model='gpt-4o-mini',
):
    """Suggest cosmo parameters based on current context.

    This is a stub function for future implementation.
    """
    import oa

    def describe_data(x):
        if isinstance(x, str):
            description = data
        elif isinstance(x, pd.DataFrame):
            description = info_extractor(x)
        else:
            description = ''
        return description

    ai_func = oa.prompt_json_function(
        cosmo_param_suggestion_prompt_template + extra_instructions,
        json_schema=cosmo_dataset_viz_params_output_schema,
        model=model,
    )

    ai_kwargs = dict(
        data_description=describe_data(data),
        n_suggestions=n_suggestions,
        points_description=describe_data(points),
        links_description=describe_data(links),
    )

    return ai_func(**ai_kwargs)


from typing import Iterable


def insert_visualizations_in_notebook(
    notebook, visualizations: Iterable | dict, insert_at_cell_index=None
):
    """Insert visualization summary & code cells into a notebook.

    Args:
        notebook: Path to the notebook file. Created if missing.
        visualizations: Iterable of visualization specs or a dict containing a
            ``visualizations`` key (per cosmo_dataset_viz_params_output_schema).
        insert_at_cell_index: Optional index where cells should be inserted.
            Defaults to appending to the end of the notebook.
    """

    def _load_notebook(nb_path: Path):
        if nb_path.exists():
            return nbformat.read(nb_path, as_version=4)
        nb_path.parent.mkdir(parents=True, exist_ok=True)
        return nbf.new_notebook(cells=[])

    def _as_visualization_list(spec):
        if isinstance(spec, dict) and "visualizations" in spec:
            spec = spec["visualizations"]
        if not isinstance(spec, Iterable) or isinstance(spec, (str, bytes)):
            raise TypeError(
                "visualizations must be iterable or contain a 'visualizations' key"
            )
        return list(spec)

    def _format_value(value):
        if isinstance(value, str):
            return json.dumps(value, ensure_ascii=False)
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return repr(value)
        if isinstance(value, bool):
            return "True" if value else "False"
        if value is None:
            return "None"
        return json.dumps(value, ensure_ascii=False)

    notebook_path = Path(notebook)
    nb = _load_notebook(notebook_path)

    vis_list = _as_visualization_list(visualizations)
    if not vis_list:
        return nb  # Nothing to insert

    cells_to_insert = []
    for vis in vis_list:
        title = vis.get("title", "Visualization")
        explanation_md = (vis.get("explanation_md") or "").strip()
        markdown_lines = [f"### {title}"]
        if explanation_md:
            markdown_lines.extend(["", explanation_md])
        markdown_cell = nbf.new_markdown_cell("\n".join(markdown_lines))
        cells_to_insert.append(markdown_cell)

        kwargs = {}
        for section in ("mappings", "cosmo_params"):
            section_values = vis.get(section) or {}
            if isinstance(section_values, dict):
                for key, value in section_values.items():
                    if value is not None:
                        kwargs[key] = value

        code_lines = ["cosmo(", "    data,"]
        if vis.get("visualization_type") == "graph":
            code_lines.append("    links=links,")
        for key, value in kwargs.items():
            code_lines.append(f"    {key}={_format_value(value)},")
        code_lines.append(")")
        code_cell = nbf.new_code_cell("\n".join(code_lines))
        cells_to_insert.append(code_cell)

    insert_index = insert_at_cell_index
    if insert_index is None or insert_index > len(nb.cells):
        insert_index = len(nb.cells)
    nb.cells[insert_index:insert_index] = cells_to_insert

    nbformat.write(nb, notebook_path)
    return nb
