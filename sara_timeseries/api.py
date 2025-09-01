from typing import List, Dict

from fastapi import APIRouter, FastAPI, HTTPException
from loguru import logger
from omnia_timeseries.api import MessageModel
from omnia_timeseries.models import TimeseriesModel

from sara_timeseries.models import (
    RequestModel,
    ResponseModel,
    DatapointsRequestModel,
    DatapointsResponseModel,
)
from sara_timeseries.omnia_service import OmniaService


class OmniaAPI:
    def __init__(self, omnia_service: OmniaService):
        self.router = APIRouter()
        self.omnia_service = omnia_service
        self.setup_routes()

    def setup_routes(self) -> None:
        @self.router.post("/datapoint")
        def forward_data(data: RequestModel) -> ResponseModel:
            try:
                id: str = self.omnia_service.get_or_add_timeseries(
                    name=data.name,
                    facility=data.facility,
                    externalId=data.externalId,
                    description=data.description,
                    unit=data.unit,
                    assetId=data.assetId,
                    step=data.step,
                    metadata=data.metadata,
                )
            except Exception as e:
                logger.error(f"Failed to get or add timeseries: {e}")
                raise HTTPException(
                    status_code=500, detail="Failed to get or add timeseries"
                )

            if not id:
                logger.error("Failed to get or add timeseries: ID is None")
                raise HTTPException(
                    status_code=500, detail="Failed to get or add timeseries"
                )

            try:
                response: MessageModel = self.omnia_service.add_datapoint_to_timeseries(
                    id, data.value, data.timestamp
                )
                logger.info(
                    f"Successfully uploaded datapoint to timeseries"
                    f" with response: {response};"
                    f" and timeseries with ID: {id}, name: {data.name}, facility: {data.facility}, description: {data.description}; "
                    f" and datapoint with value: {data.value}, timestamp: {data.timestamp}"
                )
            except Exception as e:
                logger.error(f"Failed to add datapoint to timeseries: {e}")
                raise HTTPException(
                    status_code=500, detail="Failed to add datapoint to timeseries"
                )

            return ResponseModel(
                timeseriesId=id,
                statusCode=response["statusCode"],
                message=response["message"],
            )

        @self.router.post("/get-co2-measurements")
        def get_co2_measurements(
            request: DatapointsRequestModel,
        ) -> DatapointsResponseModel:
            co2_measurements_description: str = "CO2Measurement"
            try:
                timeseries: List[TimeseriesModel] = (
                    self.omnia_service.read_timeseries_by_description_and_facility(
                        description=co2_measurements_description,
                        facility=request.facility,
                    )
                )
            except Exception:
                logger.error(
                    f"Failed to retrieve timeseries for description {co2_measurements_description} "
                    f"and facility {request.facility}"
                )
                raise HTTPException(
                    status_code=500, detail="Failed to retrieve all timeseries"
                )

            try:
                data: List[Dict] = (
                    self.omnia_service.read_data_from_multiple_timeseries(
                        timeseries=timeseries,
                        start_time=request.start_time,
                        end_time=request.end_time,
                    )
                )
                return DatapointsResponseModel(data=data)

            except Exception:
                logger.error("Failed to retrieve data from CO2 measurement timeseries")
                raise HTTPException(
                    status_code=500,
                    detail="Failed to retrieve data from CO2 measurement timeseries",
                )

    def include_in_app(self, app: FastAPI) -> None:
        app.include_router(self.router)
