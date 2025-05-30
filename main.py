import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI

from sara_omnia.api import OmniaAPI
from sara_omnia.logger import setup_logger
from sara_omnia.omnia_service import OmniaService

setup_logger()
# from loguru import logger

load_dotenv()

CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
TENANT_ID = os.environ.get("TENANT_ID")
PORT = os.environ.get("PORT")
HOST = os.environ.get("HOST")

if not CLIENT_ID or not CLIENT_SECRET or not TENANT_ID:
    raise RuntimeError(
        "CLIENT_ID, CLIENT_SECRET, and TENANT_ID must be provided via environment variables."
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
    uvicorn.run("main:app", host=HOST, port=PORT, reload=True)
