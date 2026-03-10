import json
import math
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List
from unittest.mock import MagicMock
import webbrowser

import pandas as pd
import pytest
from pandas.core.interchange.dataframe_protocol import DataFrame
from pytest_mock import MockerFixture

from sara_timeseries.modules.sara_timeseries_api.models import DatapointsResponseModel
from sara_timeseries.modules.sara_timeseries_insights.insights_service import (
    InsightsService,
)
from sara_timeseries.modules.sara_timeseries_insights.models import (
    InsightsRequest,
)
from sara_timeseries.modules.sara_timeseries_insights.visualize_gas_concentration import (
    MapCorners,
    Position,
)


@pytest.fixture
def insights_service() -> InsightsService:
    timeseries_service_mock = MagicMock()

    class MockInsightsService(InsightsService):
        def __init__(self) -> None:
            self.timeseries_service = timeseries_service_mock

    insights_service = MockInsightsService()
    return insights_service


def test_consolidate_co2_measurements(insights_service: InsightsService) -> None:
    co2_measurements_test_data: List[Dict] = _read_co2_test_data()
    insights_service.timeseries_service.get_co2_measurements.return_value = (  # type: ignore
        DatapointsResponseModel(data=co2_measurements_test_data)
    )

    request: InsightsRequest = InsightsRequest(
        facility="FACILITY",
        start_time=datetime.now(timezone.utc),
        end_time=datetime.now(timezone.utc),
    )
    df: DataFrame = insights_service.consolidate_co2_measurements(
        facility=request.facility,
        start_time=request.start_time,
        end_time=request.end_time,
    )

    assert df.shape[0] == 1
    assert math.isclose(df.loc[0, "value_mean"], 1.2139, abs_tol=0.01)
    assert math.isclose(df.loc[0, "value_median"], 0.6662, abs_tol=0.01)
    assert math.isclose(df.loc[0, "value_max"], 3.5481, abs_tol=0.01)
    assert math.isclose(df.loc[0, "value_min"], 0.0548, abs_tol=0.01)
    assert math.isclose(df.loc[0, "value_p95"], 3.1253, abs_tol=0.01)
    assert math.isclose(df.loc[0, "value_p75"], 1.7461, abs_tol=0.01)


def _read_co2_test_data() -> List[Dict]:
    data: List[Dict]
    with open(
        os.path.join(os.path.dirname(__file__), "test_data", "co2_measurements.json"),
        "r",
    ) as f:
        data = json.load(f)

    return data


def mock_get_map_and_corners() -> tuple[bytes, MapCorners]:
    corners = MapCorners(
        top_left=Position(east=68, north=322),
        top_right=Position(east=374, north=322),
        bottom_left=Position(east=68, north=90),
        bottom_right=Position(east=374, north=90),
    )
    image_jpg: bytes = Path(
        "tests/modules/sara_timeseries_insights/test_data/map.jpeg"
    ).read_bytes()

    return image_jpg, corners


def mock_consolidate_co2_measurements() -> DataFrame:
    with open(
        "tests/modules/sara_timeseries_insights/test_data/consolidated_co2_timeseries.json",
        "r",
    ) as fh:
        rows: List[Dict[str, object]] = json.load(fh)
    df_example = pd.DataFrame(rows)
    df_example = df_example[df_example["robot_name"] == "ROBOTNAME"]
    return df_example


def test_create_html_report(
    insights_service: InsightsService, mocker: MockerFixture
) -> None:
    mocker.patch.object(
        insights_service,
        "consolidate_co2_measurements",
        return_value=mock_consolidate_co2_measurements(),
    )
    mocker.patch(
        "sara_timeseries.modules.sara_timeseries_insights.insights_service.get_map_and_corners",
        lambda facility: mock_get_map_and_corners(),
    )

    html: bytes = insights_service.create_CO2_report(
        facility="FACILITY",
        start_time=datetime.now(timezone.utc),
        end_time=datetime.now(timezone.utc),
    )

    assert html is not None


@pytest.mark.skip(reason="Manual test that generates a HTML page")
def test_view_co2_report(
    insights_service: InsightsService, mocker: MockerFixture
) -> None:
    mocker.patch.object(
        insights_service,
        "consolidate_co2_measurements",
        return_value=mock_consolidate_co2_measurements(),
    )
    mocker.patch(
        "sara_timeseries.modules.sara_timeseries_insights.insights_service.get_map_and_corners",
        lambda facility: mock_get_map_and_corners(),
    )
    html_bytes: bytes = insights_service.create_CO2_report(
        facility="FACILITY",
        start_time=datetime.now(timezone.utc),
        end_time=datetime.now(timezone.utc),
    )
    html_string = html_bytes.decode("utf-8")

    filename = "co2_aggregates.html"
    with open(filename, "w") as fh:
        fh.write(html_string)
    path = os.path.abspath(filename)
    url = "file://" + path
    webbrowser.open(url)
