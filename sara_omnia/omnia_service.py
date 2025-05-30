from datetime import datetime

from azure.identity import ClientSecretCredential

# setup_logger()
from loguru import logger
from omnia_timeseries.api import (
    DatapointModel,
    DatapointsPostRequestModel,
    TimeseriesAPI,
    TimeseriesEnvironment,
    TimeseriesRequestItem,
)

# from sara_omnia.logger import setup_logger


TIMESERIES_STATUS_GOOD = 192


class OmniaService:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        tenant_id: str,
        environment=TimeseriesEnvironment.Test(),
    ):
        """
        Initializes the OmniaService with Azure credentials.
        """
        credentials = ClientSecretCredential(
            client_id=client_id,
            client_secret=client_secret,
            tenant_id=tenant_id,
        )
        self.api = TimeseriesAPI(azure_credential=credentials, environment=environment)

    def get_or_add_timeseries(
        self,
        name: str,  #  xxEyyNzzU_inspectionDescription_tagId_robotName
        facility: str,  # installation_code
        externalId: str,  # inspection_id
        description: str,  # inspection_type
        unit: str,  # unit
        assetId: str,  # installation_code?
        step: bool = True,
        metadata: dict = {},  # {"isar_id": isar_id, "tag_id": tag_id, "inspection_description", "robot_name": robot_name, "x": x, "y": y, "z": z}
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
            response = self.api.get_or_add_timeseries([timeSeriesRequestItem])
            if response["data"]["items"]:
                return response["data"]["items"][0]["id"]
            else:
                raise ValueError("No items returned in response")
        except Exception as e:
            logger.error(f"Error retrieving or adding timeseries: {e}")
            raise

    def add_datapoint_to_timeseries(
        self, id: str, value: float, timestamp: datetime
    ) -> dict:
        """
        Writes data to the timeseries with the given ID.
        Returns the response from the API.
        """
        timestamp_str = timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")
        datapoint = DatapointModel(
            time=timestamp_str,
            value=value,
            status=TIMESERIES_STATUS_GOOD,
        )
        data = DatapointsPostRequestModel(datapoints=[datapoint])
        try:
            response = self.api.add_datapoint_to_timeseries(id, data)
            return response
        except Exception as e:
            logger.error(f"Error writing data to timeseries {id}: {e}")
            raise

    def cleanup_timeseries(self, id: str) -> None:
        """
        Cleans up the timeseries with the given ID.
        Deletes the timeseries from the API.
        """
        # TODO: Remove when we use PROD environment
        try:
            response = self.api.delete_timeseries_by_id(id)
            logger.info(f"Successfully deleted timeseries {id}: {response}")
        except Exception as e:
            logger.error(f"Error deleting timeseries {id}: {e}")
            raise
