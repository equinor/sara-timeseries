import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI

from sara_timeseries.api import API
from sara_timeseries.core.settings import settings
from sara_timeseries.logger import setup_logger
from sara_timeseries.modules.sara_timeseries_api.omnia_service import OmniaService
from sara_timeseries.modules.sara_timeseries_api.timeseries_controller import (
    TimeseriesController,
)
from sara_timeseries.modules.sara_timeseries_api.timeseries_service import (
    TimeseriesService,
)

setup_logger()

load_dotenv()

if not settings.CLIENT_SECRET:
    raise RuntimeError(
        "SARA_TIMESERIES_CLIENT_SECRET must be provided as an environment variable"
    )

# Services
omnia_service = OmniaService(
    client_id=settings.CLIENT_ID,
    client_secret=settings.CLIENT_SECRET,
    tenant_id=settings.TENANT_ID,
)
timeseries_service: TimeseriesService = TimeseriesService(omnia_service=omnia_service)

# Controllers & API
timeseries_controller: TimeseriesController = TimeseriesController(
    timeseries_service=timeseries_service
)
api: API = API(timeseries_controller=timeseries_controller)

app: FastAPI = api.create_app()

if __name__ == "__main__":
    # Forcing uvicorn to run on 0.0.0.0
    uvicorn.run(
        "main:app",
        host=settings.FAST_API_HOST,
        port=settings.FAST_API_PORT,
        reload=True,
    )
