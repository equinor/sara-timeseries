import numpy as np
import pandas as pd
from pandas import DataFrame, Series

from sara_timeseries.modules.sara_timeseries_api.models import (
    DatapointsRequestModel,
)
from sara_timeseries.modules.sara_timeseries_api.timeseries_service import (
    TimeseriesService,
)
from sara_timeseries.modules.sara_timeseries_insights.models import InsightsRequest


def _percentile(x: Series, percentile: float) -> float:
    return np.percentile(x, percentile) if len(x) else np.nan


def _mean_top_percentile(x: Series, frac: float = 0.10) -> float:
    """Return the mean of the top frac proportion of values in the series."""
    n: int = max(1, int(len(x) * frac))
    return float(x.nlargest(n).mean()) if len(x) else float("nan")


def _compute_indicators(measurements: DataFrame) -> DataFrame:
    df: DataFrame = (
        measurements.groupby("name")
        .agg(
            time_min=("time", "min"),
            time_max=("time", "max"),
            description=("description", "first"),
            externalId=("externalId", "first"),
            inspection_description=("inspection_description", "first"),
            id=("id", "first"),
            facility=("facility", "first"),
            robot_name=("robot_name", "first"),
            source=("source", "first"),
            standardUnit=("standardUnit", "first"),
            status=("status", "first"),
            step=("step", "first"),
            tag_id=("tag_id", "first"),
            unit=("unit", "first"),
            # Core statistics
            value_mean=("value", "mean"),
            value_median=("value", "median"),
            value_max=("value", "max"),
            value_min=("value", "min"),
            value_std=("value", "std"),
            value_count=("value", "count"),
            value_p95=("value", lambda x: _percentile(x, 95)),
            value_p75=("value", lambda x: _percentile(x, 75)),
            value_mean_top10=("value", lambda x: _mean_top_percentile(x, 0.10)),
        )
        .reset_index()
    )

    return df


class InsightsService:
    def __init__(self, timeseries_service: TimeseriesService) -> None:
        self.timeseries_service: TimeseriesService = timeseries_service

    def consolidate_co2_measurements(self, request: InsightsRequest) -> DataFrame:
        measurements: DataFrame = pd.DataFrame(
            self.timeseries_service.get_co2_measurements(
                DatapointsRequestModel(
                    facility=request.facility,
                    start_time=request.start_time,
                    end_time=request.end_time,
                )
            ).data
        )

        measurements["time"] = pd.to_datetime(measurements["time"])
        computed_indicators: DataFrame = _compute_indicators(measurements)
        return computed_indicators
