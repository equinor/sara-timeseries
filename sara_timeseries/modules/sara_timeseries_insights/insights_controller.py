from http import HTTPStatus
from typing import Dict, List

from fastapi import APIRouter, Body, HTTPException
import logging
from pandas import DataFrame

from sara_timeseries.modules.sara_timeseries_insights.insights_service import (
    InsightsService,
)
from sara_timeseries.modules.sara_timeseries_insights.models import InsightsRequest
from sara_timeseries.authetication import authentication_dependency

logger = logging.getLogger(__name__)


class InsightsController:
    def __init__(self, insights_service: InsightsService) -> None:
        self.insights_service: InsightsService = insights_service

    def get_consolidated_co2_insights(
        self,
        request: InsightsRequest = Body(
            default=None,
            embed=False,
            title="SARA Timeseries Co2 Measurements",
            description="Retrieve a consolidated overview of CO2 measurements for the given facility and time window",
        ),
    ) -> List[Dict]:
        logger.info(
            f"Received request to consolidate CO2 measurements for facility {request.facility} and time window "
            f"{request.start_time.isoformat()} to {request.end_time.isoformat()}",
        )
        try:
            data: DataFrame = self.insights_service.consolidate_co2_measurements(
                request=request
            )
            data = data[data["robot_name"] != "NLSBot"]  # TODO: Remove
            return data.to_dict("records")
        except Exception:
            logger.exception("Failed to retrieve consolidated CO2 measurements")
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve consolidated CO2 measurements",
            )

    def create_insights_controller(self) -> APIRouter:
        router: APIRouter = APIRouter(tags=["insights"])

        router.add_api_route(
            path="/insights/consolidate-co2-measurements",
            endpoint=self.get_consolidated_co2_insights,
            methods=["POST"],
            dependencies=[authentication_dependency],
            summary="Retrieve consolidated CO2 measurements where the values are averaged",
            responses={
                HTTPStatus.OK.value: {
                    "description": "Successfully consolidated CO2 measurements",
                    "model": InsightsRequest,
                },
                HTTPStatus.INTERNAL_SERVER_ERROR.value: {
                    "description": "API request failed du to an internal server error"
                },
            },
        )

        return router
