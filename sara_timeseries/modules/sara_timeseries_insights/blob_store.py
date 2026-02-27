import json

from azure.identity import ClientSecretCredential
from azure.storage.blob import BlobServiceClient

from sara_timeseries.core.settings import settings
from sara_timeseries.modules.sara_timeseries_insights.visualize_gas_concentration import (
    MapCorners,
)


def get_map_and_corners(facility: str) -> tuple[bytes, MapCorners]:
    if settings.AZURE_CLIENT_SECRET is None:
        raise ValueError("Azure client secret is not set in settings")

    credentials = ClientSecretCredential(
        tenant_id=settings.TENANT_ID,
        client_id=settings.AZURE_CLIENT_ID,
        client_secret=settings.AZURE_CLIENT_SECRET,
    )

    blob_service_client = BlobServiceClient(
        account_url=settings.BLOB_STORAGE_ACCOUNT_URL, credential=credentials
    )
    container_client = blob_service_client.get_container_client(facility.lower())

    map_blob_client = container_client.get_blob_client("map.jpeg")
    map_bytes_jpg = map_blob_client.download_blob().readall()

    corners_blob_client = container_client.get_blob_client("map_corners.json")
    corners_bytes = corners_blob_client.download_blob().readall()
    corners_string = corners_bytes.decode("utf-8")
    corners_dict = json.loads(corners_string)
    corners = MapCorners.model_validate(corners_dict)

    return map_bytes_jpg, corners
