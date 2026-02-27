from __future__ import annotations

import base64
import json
import os
import re
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from pydantic import BaseModel, field_validator
import webbrowser


class Position(BaseModel):
    east: float
    north: float

    @field_validator("east", "north")
    @classmethod
    def validate_finite(cls, value: float) -> float:
        if not np.isfinite(value):
            raise ValueError("Coordinates must be finite numbers")
        return float(value)


class MapCorners(BaseModel):
    top_left: Position
    top_right: Position
    bottom_left: Position
    bottom_right: Position


INSPECTION_POSITION_REGEX = re.compile(
    r"\bE(?P<E>-?\d+(?:\.\d+)?)\b\s+\bN(?P<N>-?\d+(?:\.\d+)?)\b"
)


def parse_position_from_inspection_description(description: str) -> Optional[Position]:
    """Parse 'CO2 E### N###' → Position(east, north)"""
    regex_match: Optional[re.Match[str]] = INSPECTION_POSITION_REGEX.search(description)
    if not regex_match:
        return None
    return Position(
        east=float(regex_match.group("E")),
        north=float(regex_match.group("N")),
    )


def add_coordinate_columns_to_dataframe(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Add numeric E/N columns parsed from 'inspection_description'"""
    output: pd.DataFrame = dataframe.copy()
    parsed_positions: pd.Series = output["inspection_description"].map(
        parse_position_from_inspection_description
    )
    output["E"] = pd.to_numeric(
        [pos.east if pos else None for pos in parsed_positions], errors="coerce"
    )
    output["N"] = pd.to_numeric(
        [pos.north if pos else None for pos in parsed_positions], errors="coerce"
    )
    return output


def coerce_metrics_and_time(
    dataframe: pd.DataFrame,
    metric_columns: Iterable[str],
) -> pd.DataFrame:
    """Ensure metric columns are numeric and time columns are timezone-aware datetimes"""
    output: pd.DataFrame = dataframe.copy()
    for column in metric_columns:
        if column in output.columns:
            output[column] = pd.to_numeric(output[column], errors="coerce")
    for time_column in ("time_min", "time_max"):
        if time_column in output.columns:
            output[time_column] = pd.to_datetime(
                output[time_column], errors="coerce", utc=True
            )
    return output


def _image_bytes_to_data_uri(image_bytes_jpg: bytes) -> str:
    encoded: str = base64.b64encode(image_bytes_jpg).decode("ascii")
    return f"data:image/jpeg;base64,{encoded}"


def add_backdrop_image_to_figure(
    figure: go.Figure,
    image_bytes_jpg: bytes,
    corners: MapCorners,
    *,
    opacity: float = 0.45,
    lock_to_bounds: bool = True,
) -> Tuple[float, float, float, float]:
    """
    Place an axis-aligned floorplan using Position corners and (optionally) lock axes.
    The image is embedded as a data URI so it travels with exported HTML.
    Returns (east_min, east_max, north_min, north_max).
    """
    image_source: str = _image_bytes_to_data_uri(image_bytes_jpg)

    east_min, east_max = corners.bottom_left.east, corners.bottom_right.east
    north_min, north_max = corners.bottom_left.north, corners.top_left.north

    figure.add_layout_image(
        dict(
            source=image_source,
            xref="x",
            yref="y",
            x=east_min,
            y=north_max,
            sizex=east_max - east_min,
            sizey=north_max - north_min,
            sizing="stretch",
            opacity=opacity,
            layer="below",
        )
    )

    if lock_to_bounds:
        figure.update_xaxes(
            range=[east_min, east_max], autorange=False, constrain="domain"
        )
        figure.update_yaxes(
            range=[north_min, north_max],
            autorange=False,
            scaleanchor="x",
            scaleratio=1,
            constrain="domain",
        )

    return east_min, east_max, north_min, north_max


def set_bounds_from_point_data(figure: go.Figure, dataframe: pd.DataFrame) -> None:
    east_min, east_max = float(dataframe["E"].min()), float(dataframe["E"].max())
    north_min, north_max = float(dataframe["N"].min()), float(dataframe["N"].max())
    figure.update_xaxes(range=[east_min, east_max], autorange=False, constrain="domain")
    figure.update_yaxes(
        range=[north_min, north_max],
        autorange=False,
        scaleanchor="x",
        scaleratio=1,
        constrain="domain",
    )


# =========================
# Color & UI builders
# =========================


def compute_limits_for_color_bar(
    series: pd.Series, high_quantile: float = 0.95
) -> Tuple[float, float]:
    """
    Robust color limits with lower bound locked at 0.0 and upper bound at the given quantile.
    Ignores NaNs; returns (0.0, 1.0) if the series is empty.
    """
    numeric: pd.Series = pd.to_numeric(series, errors="coerce")
    if numeric.notna().sum() == 0:
        return 0.0, 1.0

    upper: float = float(np.nanquantile(numeric, high_quantile))
    # Avoid degenerate range (e.g., all zeros)
    if upper <= 0:
        upper = 1.0

    return 0.0, upper


def build_metric_traces_with_individual_color_bars(
    dataframe: pd.DataFrame,
    metric_columns: Sequence[str],
    *,
    custom_data: np.ndarray,
    dropdown_label_for_metric: Mapping[str, str],
    colorscale_name: str,
    color_bars: Mapping[str, Tuple[float, float]],
) -> List[go.Scattergl]:
    """
    Build one trace per metric, each with its own colorbar and dynamic cmin/cmax.
    Only the visible trace's colorbar shows; others hide with the trace.
    Hover shows only: Value, Count, E/N.
    """
    traces: List[go.Scattergl] = []
    for index, metric_column in enumerate(metric_columns):
        cmin, cmax = color_bars[metric_column]
        display_name = dropdown_label_for_metric.get(metric_column, metric_column)
        traces.append(
            go.Scattergl(
                x=dataframe["E"] + 0.5,
                y=dataframe["N"] + 0.5,
                mode="markers",
                visible=(index == 0),
                name=display_name,
                marker=dict(
                    size=10,
                    color=dataframe[metric_column],
                    colorscale=colorscale_name,
                    cmin=cmin,
                    cmax=cmax,
                    showscale=True,
                    colorbar=dict(title=display_name, x=1.02),
                    line=dict(width=0.5, color="black"),
                ),
                # Plotly property must be 'customdata'; Python variable is 'custom_data'
                customdata=custom_data,
                hovertemplate=(
                    "Value: %{marker.color:.3f} %{customdata[1]}<br>"
                    "Count: %{customdata[0]}<br>"
                    "E,N: %{x}, %{y}<extra></extra>"
                ),
            )
        )
    return traces


def build_dropdown_buttons_with_dynamic_color_bars(
    metric_columns: Sequence[str],
    *,
    title_base: str,
    dropdown_label_for_metric: Mapping[str, str],
) -> List[Dict[str, object]]:
    """Dropdown buttons that toggle visibility and update figure title to the active metric label."""
    buttons: List[Dict[str, object]] = []
    for index, metric_column in enumerate(metric_columns):
        visibility_mask = [False] * len(metric_columns)
        visibility_mask[index] = True
        label = dropdown_label_for_metric.get(metric_column, metric_column)
        buttons.append(
            dict(
                label=label,
                method="update",
                args=[
                    {"visible": visibility_mask},
                    {"title.text": f"{title_base} — {label}"},
                ],
            )
        )
    return buttons


# =========================
# Orchestrator
# =========================


def make_gas_concentration_figure(
    dataframe_in: pd.DataFrame,
    *,
    metric_columns: Iterable[str] = (
        "value_mean",
        "value_max",
        "value_std",
        "value_count",
    ),
    metric_labels: Optional[Mapping[str, str]] = None,
    image_bytes_jpg: Optional[bytes] = None,
    corners: Optional[MapCorners] = None,
    title: str = "Timeseries Aggregates on Floorplan",
    colorscale_name: str = "Reds",
) -> go.Figure:
    """
    Build an interactive 2D EN plot with a dropdown to switch the coloring metric.
    Uses per-metric dynamic color ranges (0 → 95th percentile) with individual color bars.
    """
    # 1) choose metrics and coerce types
    selected_metrics: List[str] = [
        m for m in metric_columns if m in dataframe_in.columns
    ]
    if not selected_metrics:
        raise ValueError("None of the requested metrics exist in the DataFrame.")
    numeric_columns = set(selected_metrics) | {"value_min", "value_std", "value_count"}
    dataframe_numeric: pd.DataFrame = coerce_metrics_and_time(
        dataframe_in, numeric_columns
    )
    dataframe: pd.DataFrame = add_coordinate_columns_to_dataframe(dataframe_numeric)

    earliest_date = pd.to_datetime(dataframe["time_min"]).min()
    latest_date = pd.to_datetime(dataframe["time_max"]).max()

    date_range_text = f"Date range: {earliest_date.date()} → {latest_date.date()}"

    # 2) hover: only count (value comes from marker.color; coords are x/y)
    custom_data_columns: Sequence[str] = ("value_count", "unit")
    custom_data = dataframe[list(custom_data_columns)].astype(object).to_numpy()

    # 3) build figure + bounds/backdrop
    figure = go.Figure()
    if image_bytes_jpg is not None and corners is not None:
        add_backdrop_image_to_figure(
            figure, image_bytes_jpg, corners, opacity=1, lock_to_bounds=True
        )
    else:
        set_bounds_from_point_data(figure, dataframe)

    # 4) human-friendly dropdown labels
    dropdown_label_for_metric: Dict[str, str] = {
        "value_mean": "Mean",
        "value_max": "Max",
        "value_std": "Std Dev",
        **(metric_labels or {}),
    }

    # 5) Fixed color ranges for consistency between runs
    # These values set where "OrRd" becomes dark.
    color_bars: Dict[str, Tuple[float, float]] = {}

    for metric in selected_metrics:
        if metric == "value_mean":
            # Light 0.07–0.09, dark > 0.1
            color_bars[metric] = (0.07, 0.14)
        elif metric == "value_max":
            # Dark > 0.5
            color_bars[metric] = (0.0, 1.0)
        elif metric == "value_std":
            # Dark > 0.01
            color_bars[metric] = (0.0, 0.02)
        else:
            # Fallback to dynamic 95th percentile
            color_bars[metric] = compute_limits_for_color_bar(dataframe[metric])

    # 6) traces (each owns its color bar)
    traces: List[go.Scattergl] = build_metric_traces_with_individual_color_bars(
        dataframe,
        selected_metrics,
        custom_data=custom_data,
        dropdown_label_for_metric=dropdown_label_for_metric,
        colorscale_name=colorscale_name,
        color_bars=color_bars,
    )
    figure.add_traces(traces)

    # 7) dropdown UI
    buttons: List[Dict[str, object]] = build_dropdown_buttons_with_dynamic_color_bars(
        selected_metrics,
        title_base=title,
        dropdown_label_for_metric=dropdown_label_for_metric,
    )

    # 8) layout
    first_label: str = dropdown_label_for_metric[selected_metrics[0]]
    figure.update_layout(
        title_text=f"{title} — {first_label}",
        title_x=0.5,
        template="plotly_white",
        margin=dict(l=40, r=90, t=110, b=40),
        xaxis_title="East (m)",
        yaxis_title="North (m)",
        updatemenus=[
            dict(
                type="dropdown",
                direction="down",
                showactive=True,
                x=0,
                y=0.95,
                xanchor="left",
                yanchor="top",
                borderwidth=1,
                buttons=buttons,
            )
        ],
        annotations=[
            dict(
                text=date_range_text,
                x=0.5,
                y=1.01,
                xref="paper",
                yref="paper",
                xanchor="center",
                yanchor="bottom",
                showarrow=False,
                font=dict(size=12, color="gray"),
            )
        ],
    )
    return figure


# =========================
# Example usage
# =========================


def generate_gas_visualization_html(
    dataframe: pd.DataFrame, image_bytes_jpg: bytes, corners: MapCorners
) -> bytes:
    fig = make_gas_concentration_figure(
        dataframe,
        metric_columns=(
            "value_mean",
            "value_max",
            "value_std",
        ),
        image_bytes_jpg=image_bytes_jpg,
        corners=corners,
        title="CO₂ Measurement Aggregates (E-N view)",
        colorscale_name="OrRd",
    )

    # Show or export
    # fig.show()
    # pio.write_html(fig, file="co2_aggregates.html", auto_open=True)

    fig_html_string = fig.to_html(full_html=True, include_plotlyjs="cdn")
    fig_html_bytes = fig_html_string.encode("utf-8")

    return fig_html_bytes


if __name__ == "__main__":
    with open(
        "sara_timeseries/modules/sara_timeseries_insights/consolidated_co2_timeseries.json",
        "r",
    ) as fh:
        rows: List[Dict[str, object]] = json.load(fh)
    df_example = pd.DataFrame(rows)
    df_example = df_example[df_example["robot_name"] == "ROBOTNAME"]

    corners = MapCorners(
        top_left=Position(east=68, north=322),
        top_right=Position(east=374, north=322),
        bottom_left=Position(east=68, north=90),
        bottom_right=Position(east=374, north=90),
    )
    image_bytes_jpg = Path(
        "sara_timeseries/modules/sara_timeseries_insights/map.jpeg"
    ).read_bytes()

    fig_html_bytes = generate_gas_visualization_html(
        df_example, image_bytes_jpg=image_bytes_jpg, corners=corners
    )
    fig_html_string = fig_html_bytes.decode("utf-8")

    filename = "co2_aggregates.html"
    with open(filename, "w") as fh:
        fh.write(fig_html_string)
    path = os.path.abspath(filename)
    url = "file://" + path
    webbrowser.open(url)
