import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI

from sara_timeseries.api import OmniaAPI
from sara_timeseries.logger import setup_logger
from sara_timeseries.omnia_service import OmniaService

setup_logger()

load_dotenv()

CLIENT_ID = os.environ.get("TIMESERIES_CLIENT_ID")
CLIENT_SECRET = os.environ.get("TIMESERIES_CLIENT_SECRET")
TENANT_ID = os.environ.get("TIMESERIES_TENANT_ID")
PORT = int(os.environ.get("PORT", 8200))

if not CLIENT_ID or not CLIENT_SECRET or not TENANT_ID:
    raise RuntimeError(
        "TIMESERIES_CLIENT_ID, TIMESERIES_CLIENT_SECRET, TIMESERIES_TENANT_ID must be provided via environment variables."
    )

# Create FastAPI app and setup routes
app = FastAPI()
omnia_service = OmniaService(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    tenant_id=TENANT_ID,
)
omnia_api = OmniaAPI(omnia_service=omnia_service)
omnia_api.include_in_app(app)

if __name__ == "__main__":
    # Forcing uvicorn to run on 0.0.0.0
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=True)
