import argparse
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

# Parse command-line arguments
parser = argparse.ArgumentParser(
    description="Send inspection values to Omnia Timeseries API"
)
parser.add_argument(
    "--clientId",
    required=False,
    help="Omnia client ID for authentication",
)
parser.add_argument(
    "--clientSecret",
    required=False,
    help="Omnia client secret for authentication",
)
parser.add_argument(
    "--tenantId",
    required=False,
    help="Azure tenant ID for authentication",
)
parser.add_argument(
    "--host",
    default="0.0.0.0",
    help="Host to run the FastAPI app on",
)
parser.add_argument(
    "--port",
    type=int,
    default=8000,
    help="Port to run the FastAPI app on",
)
args, unknown = parser.parse_known_args()

# Use CLI args if provided, otherwise fall back to environment variables
CLIENT_ID = args.clientId or os.environ.get("CLIENT_ID")
CLIENT_SECRET = args.clientSecret or os.environ.get("CLIENT_SECRET")
TENANT_ID = args.tenantId or os.environ.get("TENANT_ID")

if not CLIENT_ID or not CLIENT_SECRET or not TENANT_ID:
    raise RuntimeError(
        "CLIENT_ID, CLIENT_SECRET, and TENANT_ID must be provided via arguments or environment variables."
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
    uvicorn.run("main:app", host=args.host, port=args.port, reload=True)
