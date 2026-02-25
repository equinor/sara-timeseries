import json
import math
import os
from datetime import datetime, timezone
from typing import Dict, List
from unittest.mock import MagicMock

import pytest
from pandas.core.interchange.dataframe_protocol import DataFrame

from sara_timeseries.modules.sara_timeseries_api.models import DatapointsResponseModel
from sara_timeseries.modules.sara_timeseries_insights.insights_service import (
    InsightsService,
)
from sara_timeseries.modules.sara_timeseries_insights.models import (
    InsightsRequest,
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
    df: DataFrame = insights_service.consolidate_co2_measurements(request=request)

    assert df.shape[0] == 1
    assert math.isclose(df.loc[0, "value_mean"], 1.2999, abs_tol=0.01)
    assert math.isclose(df.loc[0, "value_median"], 0.72, abs_tol=0.01)
    assert math.isclose(df.loc[0, "value_max"], 3.5481, abs_tol=0.01)
    assert math.isclose(df.loc[0, "value_min"], 0.05481, abs_tol=0.01)
    assert math.isclose(df.loc[0, "value_p95"], 3.1856, abs_tol=0.01)
    assert math.isclose(df.loc[0, "value_p75"], 1.9440, abs_tol=0.01)


def _read_co2_test_data() -> List[Dict]:
    data: List[Dict]
    with open(
        os.path.join(os.path.dirname(__file__), "test_data", "co2_measurements.json"),
        "r",
    ) as f:
        data = json.load(f)

    return data
