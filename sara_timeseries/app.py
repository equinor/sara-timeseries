import os
import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from sara_timeseries.api import API
from sara_timeseries.core.settings import settings
from sara_timeseries.core.logger import setup_logger
from sara_timeseries.core.open_telemetry import setup_open_telemetry
from sara_timeseries.modules.sara_timeseries_api.omnia_service import OmniaService
from sara_timeseries.modules.sara_timeseries_api.timeseries_controller import (
    TimeseriesController,
)
from sara_timeseries.modules.sara_timeseries_api.timeseries_service import (
    TimeseriesService,
)
from sara_timeseries.modules.sara_timeseries_insights.insights_controller import (
    InsightsController,
)
from sara_timeseries.modules.sara_timeseries_insights.insights_service import (
    InsightsService,
)

setup_logger()
logger = logging.getLogger(__name__)

if not settings.CLIENT_SECRET:
    raise RuntimeError(
        "SARA_TIMESERIES_CLIENT_SECRET must be provided as an environment variable"
    )

USE_MOCK = os.getenv("USE_MOCK_TIMESERIES_API", "false").lower() == "true"

# Services
omnia_service = OmniaService(
    client_id=settings.CLIENT_ID,
    client_secret=settings.CLIENT_SECRET,
    tenant_id=settings.TENANT_ID,
)

if USE_MOCK:
    import timeseries_mock.http_timeseries_api as mock_api

    omnia_service.api = mock_api.HttpTimeseriesAPI(base_url="http://127.0.0.1:5001")

timeseries_service: TimeseriesService = TimeseriesService(omnia_service=omnia_service)
insights_service: InsightsService = InsightsService(
    timeseries_service=timeseries_service
)
# Controllers & API
timeseries_controller: TimeseriesController = TimeseriesController(
    timeseries_service=timeseries_service
)
insights_controller: InsightsController = InsightsController(
    insights_service=insights_service
)
api: API = API(
    timeseries_controller=timeseries_controller, insights_controller=insights_controller
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    setup_open_telemetry(app)
    logger.info("OpenTelemetry setup complete.")
    yield


app: FastAPI = api.create_app(lifespan=lifespan)
