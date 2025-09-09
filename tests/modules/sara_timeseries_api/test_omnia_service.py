from datetime import datetime
from unittest.mock import MagicMock, Mock

import pytest
from omnia_timeseries.api import MessageModel

from sara_timeseries.modules.sara_timeseries_api.omnia_service import OmniaService


@pytest.fixture
def omnia_service() -> OmniaService:
    mock_api = MagicMock()

    class MockOmniaService(OmniaService):
        def __init__(self) -> None:
            self.api = mock_api

    omnia_service = MockOmniaService()
    return omnia_service


def test_get_or_add_timeseries(omnia_service: OmniaService) -> None:
    mock_response = {"data": {"items": [{"id": "test_timeseries_id"}]}}
    omnia_service.api.get_or_add_timeseries.return_value = mock_response

    result = omnia_service.get_or_add_timeseries(
        name="test_name",
        facility="test_facility",
        external_id="test_external_id",
        description="test_description",
        unit="test_unit",
        asset_id="test_asset_id",
        metadata={"key": "value"},
    )

    assert result == "test_timeseries_id"
    omnia_service.api.get_or_add_timeseries.assert_called_once()


def test_add_datapoint_to_timeseries(omnia_service: OmniaService) -> None:
    mock_response = MessageModel(
        statusCode=0, message="test_message", traceId="test_trace_id"
    )
    omnia_service.api.write_data = Mock(return_value=mock_response)

    result = omnia_service.add_datapoint_to_timeseries(
        timeseries_id="test_id",
        value=123.45,
        timestamp=datetime(2023, 1, 1, 12, 0, 0),
    )

    assert result == mock_response
    omnia_service.api.write_data.assert_called_once()
