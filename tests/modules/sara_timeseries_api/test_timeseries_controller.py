from datetime import datetime, timedelta
from typing import Dict
from unittest.mock import MagicMock, Mock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from omnia_timeseries.api import MessageModel
from omnia_timeseries.models import (
    GetTimeseriesResponseModel,
    TimeseriesModel,
    AggregateModel,
    GetAggregatesResponseModel,
)

from sara_timeseries.api import API
from sara_timeseries.modules.sara_timeseries_api.omnia_service import OmniaService
from sara_timeseries.modules.sara_timeseries_api.timeseries_controller import (
    TimeseriesController,
)
from sara_timeseries.modules.sara_timeseries_api.timeseries_service import (
    TimeseriesService,
)

facility: str = "asset"
description: str = "CO2Measurement"
robot_name: str = "robot"
tag_id: str = "tag_id"
inspection_description: str = "CO2-E100-N100"
timestamp: str = "2025-08-28T12:31:33.7180000Z"
example_id: str = "da6f5c45-16b9-429f-8b29-b53bf701dcb0"

search_timeseries_inner_value: TimeseriesModel = {
    "assetId": facility,
    "changedTime": timestamp,
    "createdTime": timestamp,
    "description": description,
    "externalId": "",
    "facility": facility,
    "id": example_id,
    "metadata": {
        "inspection_description": inspection_description,
        "robot_name": robot_name,
        "tag_id": tag_id,
    },
    "name": f"{facility}_100E_100N_100U_{tag_id}_{robot_name}_{inspection_description}",
    "source": "FLOTILLA",
    "step": True,
    "unit": "% v/v",
}

datapoint: AggregateModel = {"time": timestamp, "value": 1, "status": 192}
get_multi_datapoint_return_value: GetAggregatesResponseModel = {
    "data": {
        "items": [
            {
                "id": "test_id",
                "datapoints": [datapoint, datapoint, datapoint, datapoint],
            }
        ]
    },
    "count": None,
    "continuationToken": None,
}

search_timeseries_return_value: GetTimeseriesResponseModel = {
    "data": {"items": [search_timeseries_inner_value, search_timeseries_inner_value]},
    "count": None,
    "continuationToken": None,
}

get_timeseries_by_id_return_value: GetTimeseriesResponseModel = {
    "data": {"items": [search_timeseries_inner_value]},
    "count": None,
    "continuationToken": None,
}


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

    omnia_service.api.search_timeseries = Mock(
        return_value=search_timeseries_return_value
    )
    omnia_service.api.get_timeseries_by_id = Mock(
        return_value=get_timeseries_by_id_return_value
    )
    omnia_service.api.get_multi_datapoints = Mock(
        return_value=get_multi_datapoint_return_value
    )

    return omnia_service


@pytest.fixture
def test_client(mock_omnia_service: OmniaService) -> TestClient:
    timeseries_service: TimeseriesService = TimeseriesService(
        omnia_service=mock_omnia_service
    )
    timeseries_controller = TimeseriesController(timeseries_service=timeseries_service)
    api: API = API(timeseries_controller=timeseries_controller)
    app: FastAPI = api.create_app()
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

    response = test_client.post("/timeseries/datapoint", json=request_payload)
    assert response.status_code == 200
    omnia_response = MessageModel(
        statusCode=0, message="test_message", traceId="test_trace_id"
    )
    assert response.json() == {
        "timeseriesId": "test_timeseries_id",
        "statusCode": omnia_response["statusCode"],
        "message": omnia_response["message"],
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

    response = test_client.post("/timeseries/datapoint", json=request_payload)
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

    response = test_client.post("/timeseries/datapoint", json=request_payload)
    assert response.status_code == 500
    assert response.json() == {"detail": "Failed to ingest data"}


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

    response = test_client.post("/timeseries/datapoint", json=request_payload)
    assert response.status_code == 500
    assert response.json() == {"detail": "Failed to ingest data"}


def test_get_datapoints_for_all_timeseries_matching_facility_and_description(
    test_client: TestClient,
    mock_omnia_service: OmniaService,
) -> None:
    payload: Dict = {
        "facility": facility,
        "start_time": (
            datetime.fromisoformat(timestamp) - timedelta(weeks=1)
        ).isoformat(),
        "end_time": (
            datetime.fromisoformat(timestamp) + timedelta(weeks=1)
        ).isoformat(),
    }

    response = test_client.post("/timeseries/get-co2-measurements", json=payload)
    output: Dict = response.json()
    assert response.status_code == 200
    assert len(output["data"]) == len(
        get_multi_datapoint_return_value["data"]["items"][0]["datapoints"]
    )
