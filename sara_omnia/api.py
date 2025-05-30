from fastapi import APIRouter
from loguru import logger

from sara_omnia.models import RequestModel
from sara_omnia.omnia_service import OmniaService


class OmniaAPI:
    def __init__(self, omnia_service: OmniaService):
        self.router = APIRouter()
        self.omnia_service = omnia_service
        self.setup_routes()

    def setup_routes(self):
        @self.router.post("/datapoint")
        async def forward_data(data: RequestModel):
            id = self.omnia_service.get_or_add_timeseries(
                name=data.name,
                facility=data.facility,
                externalId=data.externalId,
                description=data.description,
                unit=data.unit,
                assetId=data.assetId,
                step=data.step,
                metadata=data.metadata,
            )
            if not id:
                logger.error("Failed to get or add timeseries")
                return {"error": "Failed to get or add timeseries"}

            response = await self.omnia_service.add_datapoint_to_timeseries(
                id, data.value, data.timestamp
            )
            return response

    def include_in_app(self, app):
        app.include_router(self.router)
