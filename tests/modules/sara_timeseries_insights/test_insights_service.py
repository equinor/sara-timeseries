from datetime import datetime, timezone
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


co2_measurements_test_data = [
    {
        "changedTime": "2025-08-28T12:31:33.7185391Z",
        "createdTime": "2025-08-28T12:31:33.7185382Z",
        "description": "CO2Measurement",
        "externalId": "",
        "id": "uuid1",
        "inspection_description": "CO2 E258 N278",
        "name": "FACILITY_258E_278N_105U_TAGID_ROBOTNAME_CO2-E258-N278",
        "facility": "FACILITY",
        "robot_name": "ROBOTNAME",
        "source": "test",
        "standardUnit": None,
        "status": 192,
        "step": True,
        "tag_id": "TAGID",
        "time": "2025-07-13T02:04:22.0000000Z",
        "unit": "% v/v",
        "value": 0.5480771,
    },
    {
        "changedTime": "2025-08-28T12:31:33.7185391Z",
        "createdTime": "2025-08-28T12:31:33.7185382Z",
        "description": "CO2Measurement",
        "externalId": "",
        "id": "uuid1",
        "inspection_description": "CO2 E258 N278",
        "name": "FACILITY_258E_278N_105U_TAGID_ROBOTNAME_CO2-E258-N278",
        "facility": "FACILITY",
        "robot_name": "ROBOTNAME",
        "source": "test",
        "standardUnit": None,
        "status": 192,
        "step": True,
        "tag_id": "TAGID",
        "time": "2025-07-13T02:04:22.0000000Z",
        "unit": "% v/v",
        "value": 0.5480771,
    },
    {
        "changedTime": "2025-08-28T12:31:33.7185391Z",
        "createdTime": "2025-08-28T12:31:33.7185382Z",
        "description": "CO2Measurement",
        "externalId": "",
        "id": "uuid2",
        "inspection_description": "CO2 E258 N278",
        "name": "FACILITY_259E_278N_105U_TAGID_ROBOTNAME_CO2-E258-N278",
        "facility": "FACILITY",
        "robot_name": "ROBOTNAME",
        "source": "test",
        "standardUnit": None,
        "status": 192,
        "step": True,
        "tag_id": "TAGID",
        "time": "2025-07-13T02:05:22.0000000Z",
        "unit": "% v/v",
        "value": 0.612345,
    },
]


def test_consolidate_co2_measurements(insights_service: InsightsService) -> None:
    insights_service.timeseries_service.get_co2_measurements.return_value = (  # type: ignore
        DatapointsResponseModel(data=co2_measurements_test_data)
    )

    request: InsightsRequest = InsightsRequest(
        facility="FACILITY",
        start_time=datetime.now(timezone.utc),
        end_time=datetime.now(timezone.utc),
    )
    consolidated_measurements: DataFrame = (
        insights_service.consolidate_co2_measurements(request=request)
    )

    assert consolidated_measurements.shape[0] == 2
