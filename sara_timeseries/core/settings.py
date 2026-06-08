from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Fast API configuration
    FAST_API_HOST: str = Field(default="0.0.0.0")
    FAST_API_PORT: int = Field(default=8200)
    RELOAD: bool = Field(default=False)

    TENANT_ID: str = Field(default="3aa4a235-b6e2-48d5-9195-7fcf05b459b0")

    # Ego auth
    AZURE_CLIENT_ID: str = Field(default="dd7e115a-037e-4846-99c4-07561158a9cd")

    # Optional client secret for the sara app registration. Only consumed when
    # "ClientSecret" is included in AZURE_AUTH_METHODS (off by default).
    AZURE_CLIENT_SECRET: Optional[str] = Field(default=None)

    # Ordered list of credential types attempted when authenticating to Azure
    # resources (e.g. Blob Storage). The first one that yields a token wins;
    # subsequent entries are tried only on CredentialUnavailableError. Mirrors
    # sara's AzureAd:AllowedAuthMethods. Supported: "WorkloadIdentity",
    # "AzureCli", "ClientSecret".
    AZURE_AUTH_METHODS: list[str] = Field(
        default_factory=lambda: ["WorkloadIdentity", "AzureCli"]
    )

    # Service principle authentication
    TIMESERIES_CLIENT_ID: str = Field(default="38ab1ef9-d7ea-4e2b-ae4c-466ca70a1093")
    TIMESERIES_CLIENT_SECRET: Optional[str] = Field(default=None)
    USE_OMNIA_TIMESERIES_TEST_ENVIRONMENT: bool = Field(default=True)

    # OpenTelemetry
    OTEL_SERVICE_NAME: str = Field(default="sara-timeseries")
    OTEL_EXPORTER_OTLP_ENDPOINT: str = Field(default="http://localhost:4317")
    OTEL_EXPORTER_OTLP_PROTOCOL: str = Field(default="grpc")

    # Blob store
    BLOB_STORAGE_ACCOUNT_URL: str = Field(
        default="https://saradevstoretime.blob.core.windows.net"
    )

    # Application settings
    LIB_LOG_LEVEL: str = Field(
        default="INFO"
    )  # This does not affect the log level of uvicorn, just our own log statements and libraries that we use.

    model_config = SettingsConfigDict(
        env_prefix="SARA_TIMESERIES_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
