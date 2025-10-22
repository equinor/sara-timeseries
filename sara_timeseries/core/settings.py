from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    # Fast API configuration
    FAST_API_HOST: str = Field(default="0.0.0.0")
    FAST_API_PORT: int = Field(default=8200)

    # Service principle authentication
    CLIENT_ID: str = Field(default="38ab1ef9-d7ea-4e2b-ae4c-466ca70a1093")
    TENANT_ID: str = Field(default="3aa4a235-b6e2-48d5-9195-7fcf05b459b0")
    CLIENT_SECRET: Optional[str] = Field(default=None)

    model_config = SettingsConfigDict(
        env_prefix="SARA_TIMESERIES_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
