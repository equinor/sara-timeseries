import logging
from datetime import datetime

from azure.identity import ClientSecretCredential
from omnia_timeseries.api import (
    DatapointModel,
    DatapointsPostRequestModel,
    GetTimeseriesResponseModel,
    MessageModel,
    TimeseriesAPI,
    TimeseriesEnvironment,
    TimeseriesRequestItem,
)
from omnia_timeseries.models import (
    AggregateItemModel,
    GetAggregatesResponseModel,
    GetMultipleDatapointsRequestItem,
    TimeseriesModel,
)

from sara_timeseries.core.settings import settings

logger = logging.getLogger(__name__)

TIMESERIES_STATUS_GOOD = 192


class OmniaService:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        tenant_id: str,
        environment: TimeseriesEnvironment = (
            TimeseriesEnvironment.Test()
            if settings.USE_OMNIA_TIMESERIES_TEST_ENVIRONMENT
            else TimeseriesEnvironment.Prod()
        ),
    ) -> None:
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
        name: str,
        facility: str,
        external_id: str,
        description: str,
        unit: str,
        asset_id: str,
        step: bool = True,
        metadata: dict = {},
    ) -> str:
        """
        Retrieves or adds a timeseries
        Returns the ID of the timeseries.
        """
        time_series_request_item = TimeseriesRequestItem(
            name=name,
            facility=facility,
            externalId=external_id,
            description=description,
            unit=unit,
            step=step,
            assetId=asset_id,
            metadata=metadata,
        )
        try:
            response: GetTimeseriesResponseModel = self.api.get_or_add_timeseries(
                [time_series_request_item]
            )
            if response["data"]["items"]:
                return response["data"]["items"][0]["id"]
            else:
                raise ValueError("No items returned in response")
        except Exception as e:
            logger.error(f"Error retrieving or adding timeseries: {e}")
            raise

    def add_datapoint_to_timeseries(
        self, timeseries_id: str, value: float, timestamp: datetime
    ) -> MessageModel:
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
            x = self.api.write_data(timeseries_id, data)
            return x
        except Exception as e:
            logger.error(f"Error writing to timeseries: {e}")
            raise e

    def cleanup_timeseries(self, timeseries_id: str) -> None:
        """
        Cleans up the timeseries with the given ID.
        Deletes the timeseries from the API.
        """
        # TODO: Remove when we use PROD environment
        try:
            response = self.api.delete_timeseries_by_id(timeseries_id)
            logger.info(f"Successfully deleted timeseries {timeseries_id}: {response}")
        except Exception as e:
            logger.error(f"Error deleting timeseries {timeseries_id}: {e}")
            raise

    def read_all_timeseries_by_description(
        self, description: str
    ) -> list[TimeseriesModel]:
        """
        Reads all timeseries from the API which match the given description.
        """
        timeseries: GetTimeseriesResponseModel = self.api.search_timeseries(
            description=description
        )
        return timeseries["data"]["items"]

    def read_timeseries_by_description_and_facility(
        self, description: str, facility: str
    ) -> list[TimeseriesModel]:
        """
        Reads all timeseries from the API which match the given description and facility.
        """
        timeseries: list[TimeseriesModel] = self.read_all_timeseries_by_description(
            description
        )
        return self._filter_timeseries_by_facility(
            facility=facility, timeseries=timeseries
        )

    def read_timeseries_by_description_and_facility_and_name(
        self, description: str, facility: str, name: str
    ) -> list[TimeseriesModel]:
        """
        Reads all timeseries from the API which match the given description, facility, and name.
        """
        timeseries: GetTimeseriesResponseModel = self.api.search_timeseries(
            description=description, facility=facility, name=name
        )
        return timeseries["data"]["items"]

    def read_data_from_multiple_timeseries(
        self,
        timeseries: list[TimeseriesModel],
        start_time: datetime,
        end_time: datetime,
    ) -> list[dict]:
        """
        Reads all datapoints in the given timeseries within the given time range.
        """
        requests: list[list[GetMultipleDatapointsRequestItem]] = (
            self._build_api_requests(end_time, start_time, timeseries)
        )
        data: list[GetAggregatesResponseModel] = self._request_data_from_api(requests)
        flattened_data: list[dict] = self._flatten_data(data)

        return flattened_data

    @staticmethod
    def _filter_timeseries_by_facility(
        facility: str, timeseries: list[TimeseriesModel]
    ) -> list[TimeseriesModel]:
        return [series for series in timeseries if series.get("facility") == facility]

    @staticmethod
    def _data_request_must_be_split(
        timeseries: list[TimeseriesModel], request_limit: int
    ) -> bool:
        return True if len(timeseries) > request_limit else False

    @staticmethod
    def _split_list(data: list, n: int) -> list[list]:
        return [data[i : i + n] for i in range(0, len(data), n)]

    @staticmethod
    def _flatten_timeseries_response(d: TimeseriesModel) -> dict:
        flattened: dict = {k: v for k, v in d.items() if k != "metadata"}

        metadata: dict = d.get("metadata")
        if isinstance(metadata, dict):
            flattened.update(metadata)

        return flattened

    def _flatten_data(self, data: list[GetAggregatesResponseModel]) -> list[dict]:
        squashed_data: list[AggregateItemModel] = [
            item for d in data for item in d["data"]["items"]
        ]
        flattened_data: list[dict] = [
            {"id": d["id"], **dp}
            for d in squashed_data
            for dp in d.get("datapoints", [])
        ]
        for d in flattened_data:
            series: GetTimeseriesResponseModel = self.api.get_timeseries_by_id(d["id"])
            flattened_series: dict = self._flatten_timeseries_response(
                series["data"]["items"][0]
            )
            d.update(flattened_series)

        return flattened_data

    def _request_data_from_api(
        self, requests: list[list[GetMultipleDatapointsRequestItem]]
    ) -> list[GetAggregatesResponseModel]:
        data: list[GetAggregatesResponseModel] = [
            self.api.get_multi_datapoints(req) for req in requests
        ]
        return data

    def _build_api_requests(
        self,
        end_time: datetime,
        start_time: datetime,
        timeseries: list[TimeseriesModel],
    ) -> list[list[GetMultipleDatapointsRequestItem]]:
        timeseries_api_request_limit: int = 100
        request: list[GetMultipleDatapointsRequestItem] = [
            {
                "id": item["id"],
                "startTime": start_time.isoformat(),
                "endTime": end_time.isoformat(),
                "statusFilter": [TIMESERIES_STATUS_GOOD],
            }
            for item in timeseries
        ]

        requests: list[list[GetMultipleDatapointsRequestItem]] = [request]
        if self._data_request_must_be_split(timeseries, timeseries_api_request_limit):
            requests = self._split_list(request, timeseries_api_request_limit)

        return requests
