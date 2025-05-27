import argparse
import os
import sys
from datetime import datetime, timezone

from azure.identity import ClientSecretCredential
from dotenv import load_dotenv
from omnia_timeseries.api import (
    DatapointModel,
    DatapointsPostRequestModel,
    TimeseriesAPI,
    TimeseriesEnvironment,
    TimeseriesRequestItem,
)

from sara_omnia.logger import setup_logger

setup_logger()
from loguru import logger

from sara_omnia.utils import get_env_var_or_raise_error

CLIENT_ID = get_env_var_or_raise_error("CLIENT_ID")
CLIENT_SECRET = get_env_var_or_raise_error("CLIENT_SECRET")
TENANT_ID = get_env_var_or_raise_error("TENANT_ID")


def setup_api() -> TimeseriesAPI:
    """
    Sets up the Timeseries API client with credentials from environment variables.
    Returns an instance of TimeseriesAPI.
    """

    credentials = ClientSecretCredential(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        tenant_id=TENANT_ID,
    )

    return TimeseriesAPI(
        azure_credential=credentials, environment=TimeseriesEnvironment.Test()
    )


API = setup_api()


def get_or_add_timeseries(
    name: str,
    facility: str,
    externalId: str,
    description: str,
    unit: str,
    assetId: str,
    step: bool = True,
    metadata: dict = {},
) -> str:
    """
    Retrieves or adds a timeseries
    Returns the ID of the timeseries.
    """
    timeSeriesRequestItem = TimeseriesRequestItem(
        name=name,
        facility=facility,
        externalId=externalId,
        description=description,
        unit=unit,
        step=step,
        assetId=assetId,
        metadata=metadata,
    )
    try:
        response = API.get_or_add_timeseries([timeSeriesRequestItem])
        if response["data"]["items"]:
            return response["data"]["items"][0]["id"]
        else:
            raise ValueError("No items returned in response")
    except Exception as e:
        logger.error(f"Error retrieving or adding timeseries: {e}")
        raise


def write_data(id: str) -> dict:
    """
    Writes data to the timeseries with the given ID.
    Returns the response from the API.
    """
    # TODO: GET values from parameters or environment variables
    now_utc = datetime.now(timezone.utc)
    now_utc_str = now_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
    datapoint = DatapointModel(
        time=now_utc_str,
        value=123.45,
        status=192,
    )
    data = DatapointsPostRequestModel(datapoints=[datapoint])
    try:
        response = API.write_data(id, data)
        return response
    except Exception as e:
        logger.error(f"Error writing data to timeseries {id}: {e}")
        raise


def cleanup_timeseries(id: str) -> None:
    """
    Cleans up the timeseries with the given ID.
    Deletes the timeseries from the API.
    """
    # TODO: Remove when we use PROD environment
    try:
        response = API.delete_timeseries_by_id(id)
        logger.info(f"Successfully deleted timeseries {id}: {response}")
    except Exception as e:
        logger.error(f"Error deleting timeseries {id}: {e}")
        raise


def main():
    print(f"Got command: {sys.argv}")
    parser = argparse.ArgumentParser(
        description="Send inspection values to Omnia Timeseries API"
    )
    parser.add_argument(
        "--clientId",
        required=True,
        help="Omnia client ID for authentication",
    )
    parser.add_argument(
        "--clientSecret",
        required=True,
        help="Omnia client secret for authentication",
    )
    args = parser.parse_args()

    load_dotenv()
    CLIENT_ID = os.environ.get("TimeSeries-Test-ClientID")
    CLIENT_SECRET = os.environ.get("TimeSeries-Test-Client-Secret")
    print("CLIENT_ID:", CLIENT_ID)
    print("CLIENT_SECRET:", CLIENT_SECRET)
    credentials = ClientSecretCredential(
        client_id=os.environ["TimeSeries-Test-ClientID"],
        client_secret=os.environ["TimeSeries-Test-Client-Secret"],
        tenant_id=os.environ["AZURE_TENANT_ID"],
    )
    cleanup = True
    api = TimeseriesAPI(
        azure_credential=credentials, environment=TimeseriesEnvironment.Test()
    )

    if cleanup:
        cleanup_timeseries
    # try:
    #     raw_data_storage_location = BlobStorageLocation.model_validate(
    #         json.loads(args.rawDataBlobStorageLocation)
    #     )
    #     anonymized_storage_location = BlobStorageLocation.model_validate(
    #         json.loads(args.anonymizedBlobStorageLocation)
    #     )
    # except json.JSONDecodeError as e:
    #     raise ValueError(f"Invalid JSON provided: {e}")
    # except Exception as e:
    #     raise ValueError(f"Error parsing input: {e}")

    # process_data(raw_data_storage_location, anonymized_storage_location)


if __name__ == "__main__":
    main()
