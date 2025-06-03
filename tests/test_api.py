from unittest.mock import MagicMock, Mock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from omnia_timeseries.api import MessageModel

from sara_omnia.api import OmniaAPI
from sara_omnia.omnia_service import OmniaService


@pytest.fixture
def mock_omnia_service() -> OmniaService:
    mock_api = MagicMock()

    class MockOmniaService(OmniaService):
        def __init__(self) -> None:
            self.api = mock_api

    omnia_service = MockOmniaService()
    mock_response = {"data": {"items": [{"id": "test_timeseries_id"}]}}

    omnia_service.api.get_or_add_timeseries = Mock(return_value=mock_response)

    mock_response = MessageModel(
        statusCode=0, message="test_message", traceId="test_trace_id"
    )
    omnia_service.api.write_data = Mock(return_value=mock_response)

    return omnia_service


@pytest.fixture
def test_client(mock_omnia_service: OmniaService) -> TestClient:
    app = FastAPI()
    omnia_api = OmniaAPI(mock_omnia_service)
    omnia_api.include_in_app(app)
    return TestClient(app)


def test_datapoint_endpoint_success(test_client: TestClient) -> None:
    request_payload = {
        "name": "Test Timeseries",
        "facility": "Test Facility",
        "externalId": "12345",
        "description": "Test Description",
        "unit": "m",
        "assetId": "asset123",
        "step": True,
        "metadata": {"key": "value"},
        "value": 42.0,
        "timestamp": "2023-01-01T00:00:00Z",
    }

    response = test_client.post("/datapoint", json=request_payload)
    assert response.status_code == 200
    assert response.json() == {
        "timeseriesId": "test_timeseries_id",
        "details": MessageModel(
            statusCode=0, message="test_message", traceId="test_trace_id"
        ),
    }


def test_datapoint_endpoint_invalid_timestamp(test_client: TestClient) -> None:
    request_payload = {
        "name": "Test Timeseries",
        "facility": "Test Facility",
        "externalId": "12345",
        "description": "Test Description",
        "unit": "m",
        "assetId": "asset123",
        "step": True,
        "metadata": {"key": "value"},
        "value": 42.0,
        "timestamp": "20230101T00:00:00Z",
    }

    response = test_client.post("/datapoint", json=request_payload)
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "ctx": {
                    "error": "invalid date separator, expected `-`",
                },
                "input": "20230101T00:00:00Z",
                "loc": [
                    "body",
                    "timestamp",
                ],
                "msg": "Input should be a valid datetime or date, invalid date separator, "
                "expected `-`",
                "type": "datetime_from_date_parsing",
            },
        ],
    }


def test_datapoint_endpoint_failure_get_or_add_timeseries(
    test_client: TestClient, mock_omnia_service: OmniaService
) -> None:
    mock_omnia_service.api.get_or_add_timeseries = Mock(
        side_effect=Exception("Service error")
    )
    request_payload = {
        "name": "Test Timeseries",
        "facility": "Test Facility",
        "externalId": "12345",
        "description": "Test Description",
        "unit": "m",
        "assetId": "asset123",
        "step": True,
        "metadata": {"key": "value"},
        "value": 42.0,
        "timestamp": "2023-01-01T00:00:00Z",
    }

    response = test_client.post("/datapoint", json=request_payload)
    assert response.status_code == 500
    assert response.json() == {"detail": "Failed to get or add timeseries"}


def test_datapoint_endpoint_failure_add_datapoint(
    test_client: TestClient, mock_omnia_service: OmniaService
) -> None:
    mock_omnia_service.api.write_data = Mock(side_effect=Exception("Service error"))
    request_payload = {
        "name": "Test Timeseries",
        "facility": "Test Facility",
        "externalId": "12345",
        "description": "Test Description",
        "unit": "m",
        "assetId": "asset123",
        "step": True,
        "metadata": {"key": "value"},
        "value": 42.0,
        "timestamp": "2023-01-01T00:00:00Z",
    }

    response = test_client.post("/datapoint", json=request_payload)
    assert response.status_code == 500
    assert response.json() == {"detail": "Failed to add datapoint to timeseries"}
