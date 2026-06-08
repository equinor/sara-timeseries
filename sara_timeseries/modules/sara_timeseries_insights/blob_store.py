import json

from azure.storage.blob import BlobClient, BlobServiceClient, ContainerClient

from sara_timeseries.core.credentials import build_credential
from sara_timeseries.core.settings import settings
from sara_timeseries.modules.sara_timeseries_insights.visualize_gas_concentration import (
    MapCorners,
)


def get_map_and_corners(facility: str) -> tuple[bytes, MapCorners]:
    # In AKS, WorkloadIdentityCredential reads the federated token mounted by
    # the workload-identity webhook (the pod's service account is annotated
    # with the sara app registration client ID). Locally, AzureCliCredential
    # is used (`az login`). The chain is configurable via
    # SARA_TIMESERIES_AZURE_AUTH_METHODS; "ClientSecret" can be added when a
    # secret-based fallback is needed.
    credentials = build_credential(
        settings.AZURE_AUTH_METHODS,
        tenant_id=settings.TENANT_ID,
        client_id=settings.AZURE_CLIENT_ID,
        client_secret=settings.AZURE_CLIENT_SECRET,
    )

    blob_service_client = BlobServiceClient(
        account_url=settings.BLOB_STORAGE_ACCOUNT_URL, credential=credentials
    )
    container_client: ContainerClient = blob_service_client.get_container_client(
        facility.lower()
    )

    map_blob_client: BlobClient = container_client.get_blob_client("map.jpeg")
    map_jpg: bytes = map_blob_client.download_blob().readall()

    corners_blob_client: BlobClient = container_client.get_blob_client(
        "map_corners.json"
    )
    corners_bytes: bytes = corners_blob_client.download_blob().readall()
    corners_string: str = corners_bytes.decode("utf-8")
    corners_dict: dict = json.loads(corners_string)
    corners = MapCorners.model_validate(corners_dict)

    return map_jpg, corners
