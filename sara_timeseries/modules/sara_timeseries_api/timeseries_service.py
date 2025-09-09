from typing import List, Dict

from loguru import logger
from omnia_timeseries.models import TimeseriesModel, MessageModel

from sara_timeseries.modules.sara_timeseries_api.models import (
    DatapointsRequestModel,
    DatapointsResponseModel,
    RequestModel,
    ResponseModel,
)
from sara_timeseries.modules.sara_timeseries_api.omnia_service import OmniaService


class TimeseriesService:
    def __init__(self, omnia_service: OmniaService) -> None:
        self.omnia_service = omnia_service

    def ingest_datapoint(self, datapoint: RequestModel) -> ResponseModel:
        try:
            timeseries_id: str = self.omnia_service.get_or_add_timeseries(
                name=datapoint.name,
                facility=datapoint.facility,
                external_id=datapoint.externalId,
                description=datapoint.description,
                unit=datapoint.unit,
                asset_id=datapoint.assetId,
                step=datapoint.step,
                metadata=datapoint.metadata,
            )
        except Exception:
            logger.error("Failed to get or add timeseries")
            raise

        if not timeseries_id:
            logger.error("Failed to get or add timeseries: ID is None")
            raise

        try:
            response: MessageModel = self.omnia_service.add_datapoint_to_timeseries(
                timeseries_id, datapoint.value, datapoint.timestamp
            )
            logger.info(
                f"Successfully uploaded datapoint to timeseries with response: {response}; and timeseries "
                f"with ID: {timeseries_id}, name: {datapoint.name}, facility: {datapoint.facility}, description: "
                f"{datapoint.description}; and datapoint with value: {datapoint.value}, timestamp: "
                f"{datapoint.timestamp}"
            )
        except Exception:
            logger.error("Failed to add datapoint to timeseries")
            raise

        return ResponseModel(
            timeseriesId=timeseries_id,
            statusCode=response["statusCode"],
            message=response["message"],
        )

    def get_co2_measurements(
        self, request: DatapointsRequestModel
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
            raise

        try:
            data: List[Dict] = self.omnia_service.read_data_from_multiple_timeseries(
                timeseries=timeseries,
                start_time=request.start_time,
                end_time=request.end_time,
            )
            return DatapointsResponseModel(data=data)

        except Exception:
            logger.error("Failed to retrieve data from CO2 measurement timeseries")
            raise
