from fastapi import APIRouter, FastAPI, HTTPException
from loguru import logger
from omnia_timeseries.api import MessageModel

from sara_timeseries.models import RequestModel, ResponseModel
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
            except Exception as e:
                logger.error(f"Failed to add datapoint to timeseries: {e}")
                raise HTTPException(
                    status_code=500, detail="Failed to add datapoint to timeseries"
                )

            return ResponseModel(timeseriesId=id, details=response)

    def include_in_app(self, app: FastAPI) -> None:
        app.include_router(self.router)
