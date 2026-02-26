import logging
from fastapi import Depends, Security
from fastapi_azure_auth import SingleTenantAzureAuthorizationCodeBearer
from fastapi_azure_auth.exceptions import InvalidAuthHttp
from fastapi_azure_auth.user import User
from sara_timeseries.core.settings import settings

azure_scheme = SingleTenantAzureAuthorizationCodeBearer(
    app_client_id=settings.AZURE_CLIENT_ID,
    tenant_id=settings.TENANT_ID,
    scopes={
        f"api://{settings.AZURE_CLIENT_ID}/user_impersonation": "user_impersonation",
    },
)


async def validate_has_role(user: User = Depends(azure_scheme)) -> None:
    """
    Validate if the user has the required role in order to access the API.
    Raises a 403 authorization error if not.
    """
    if "PlantData.Read" not in user.roles:
        raise InvalidAuthHttp(
            "Current user does not possess the required role for this endpoint"
        )


authentication_dependency = Security(validate_has_role)


class Authenticator:
    def __init__(self) -> None:
        self.logger = logging.getLogger("api")
        self.logger.info("API authentication is enabled")

    async def load_config(self) -> None:
        """
        Load OpenID config on startup.
        """
        await azure_scheme.openid_config.load_config()
