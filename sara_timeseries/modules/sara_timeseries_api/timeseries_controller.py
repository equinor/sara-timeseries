from http import HTTPStatus

from fastapi import APIRouter, Body, HTTPException
import logging

from sara_timeseries.modules.sara_timeseries_api.models import (
    CO2ConcentrationRequestModel,
    RequestModel,
    ResponseModel,
    DatapointsRequestModel,
    DatapointsResponseModel,
)
from sara_timeseries.modules.sara_timeseries_api.timeseries_service import (
    TimeseriesService,
)

logger = logging.getLogger(__name__)


class TimeseriesController:
    def __init__(self, timeseries_service: TimeseriesService) -> None:
        self.timeseries_service: TimeseriesService = timeseries_service

    def ingest_data(
        self,
        data: RequestModel = Body(
            default=None,
            embed=False,
            title="SARA Timeseries Forward Data",
            description="Data to be forwarded",
        ),
    ) -> ResponseModel:
        logger.info(
            f"Received request to ingest datapoint with name {data.name} to facility {data.facility} "
            f"with timestamp {data.timestamp.isoformat()}"
        )
        try:
            return self.timeseries_service.ingest_datapoint(datapoint=data)
        except Exception:
            raise HTTPException(status_code=500, detail="Failed to ingest data")

    def get_co2_measurements(
        self,
        request: DatapointsRequestModel = Body(
            default=None,
            embed=False,
            title="SARA Timeseries Co2 Measurements",
            description="Retrieve all CO2 measurements for the given facility and time window",
        ),
    ) -> DatapointsResponseModel:
        logger.info(
            f"Received request to retrieve CO2 measurements for facility {request.facility} and time window "
            f"{request.start_time.isoformat()} to {request.end_time.isoformat()}",
        )
        try:
            return self.timeseries_service.get_co2_measurements(request)
        except Exception:
            raise HTTPException(
                status_code=500, detail="Failed to retrieve CO2 measurements"
            )

    def get_co2_concentration(
        self,
        request: CO2ConcentrationRequestModel = Body(
            default=None,
            embed=False,
            title="SARA Timeseries Co2 Concentration",
            description="Retrieve CO2 concentration for a single task",
        ),
    ) -> float:
        try:
            return self.timeseries_service.get_co2_concentration(request)
        except HTTPException as e:
            raise e
        except Exception:
            raise HTTPException(
                status_code=500, detail="Failed to retrieve CO2 concentration"
            )

    def create_timeseries_router(self) -> APIRouter:
        router: APIRouter = APIRouter(tags=["timeseries"])

        router.add_api_route(
            path="/timeseries/datapoint",
            endpoint=self.ingest_data,
            methods=["POST"],
            summary="Forward a single datapoint to be inserted into the Timeseries API",
            responses={
                HTTPStatus.OK.value: {
                    "description": "Successfully added datapoint to Timeseries API",
                    "model": ResponseModel,
                },
                HTTPStatus.INTERNAL_SERVER_ERROR.value: {
                    "description": "API request failed du to an internal server error"
                },
            },
        )

        router.add_api_route(
            path="/timeseries/get-co2-measurements",
            endpoint=self.get_co2_measurements,
            methods=["POST"],
            summary="Retrieve all CO2 measurements for the given facility and time period",
            responses={
                HTTPStatus.OK.value: {
                    "description": "Successfully retrieved datapoints from Timeseries API",
                    "model": DatapointsResponseModel,
                },
                HTTPStatus.INTERNAL_SERVER_ERROR.value: {
                    "description": "API request failed due to an internal server error"
                },
            },
        )

        router.add_api_route(
            path="/timeseries/get-co2-concentration",
            endpoint=self.get_co2_concentration,
            methods=["POST"],
            summary="Retrieve CO2 concentration for a single task using inspection name, task time range and facility",
            responses={
                HTTPStatus.OK.value: {
                    "description": "Successfully retrieved CO2 concentration from Timeseries API",
                    "model": float,
                },
                HTTPStatus.INTERNAL_SERVER_ERROR.value: {
                    "description": "API request failed due to an internal server error"
                },
                HTTPStatus.NOT_FOUND.value: {
                    "description": "No CO2 concentration found for the given inspection name, task time range and facility"
                },
                HTTPStatus.BAD_REQUEST.value: {
                    "description": "Multiple CO2 concentrations found for the given inspection name, task time range and facility"
                },
            },
        )

        return router
