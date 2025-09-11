from http import HTTPStatus

from fastapi import APIRouter, Body, HTTPException

from sara_timeseries.modules.sara_timeseries_api.models import (
    RequestModel,
    ResponseModel,
    DatapointsRequestModel,
    DatapointsResponseModel,
)
from sara_timeseries.modules.sara_timeseries_api.timeseries_service import (
    TimeseriesService,
)


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
        try:
            return self.timeseries_service.get_co2_measurements(request)
        except Exception:
            raise HTTPException(
                status_code=500, detail="Failed to retrieve CO2 measurements"
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
                    "description": "API request failed du to an internal server error"
                },
            },
        )

        return router
