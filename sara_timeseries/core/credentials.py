import os
from typing import Callable, Optional

from azure.core.credentials import TokenCredential
from azure.identity import (
    AzureCliCredential,
    ChainedTokenCredential,
    ClientSecretCredential,
    WorkloadIdentityCredential,
)

# Env vars injected by the workload-identity webhook on pods whose service
# account is annotated with ``azure.workload.identity/client-id``.
_WI_REQUIRED_ENV_VARS: tuple[str, ...] = (
    "AZURE_TENANT_ID",
    "AZURE_CLIENT_ID",
    "AZURE_FEDERATED_TOKEN_FILE",
)

_SUPPORTED_METHODS: tuple[str, ...] = ("WorkloadIdentity", "AzureCli", "ClientSecret")


def _build_workload_identity() -> Optional[TokenCredential]:
    """Return a ``WorkloadIdentityCredential`` if WI env vars are injected.

    Outside a WI-enabled pod (local dev, CI), the SDK's constructor raises
    ``ValueError`` because the required arguments are missing. Pre-check the
    env so the chain can fall through silently.
    """
    if any(not os.environ.get(v) for v in _WI_REQUIRED_ENV_VARS):
        return None
    return WorkloadIdentityCredential()


def _build_azure_cli() -> Optional[TokenCredential]:
    return AzureCliCredential()


def _build_client_secret(
    tenant_id: Optional[str],
    client_id: Optional[str],
    client_secret: Optional[str],
) -> Optional[TokenCredential]:
    """Return a ``ClientSecretCredential`` if all three values are set, else ``None``."""
    if not (tenant_id and client_id and client_secret):
        return None
    return ClientSecretCredential(
        tenant_id=tenant_id,
        client_id=client_id,
        client_secret=client_secret,
    )


def build_credential(
    methods: list[str],
    *,
    tenant_id: Optional[str] = None,
    client_id: Optional[str] = None,
    client_secret: Optional[str] = None,
) -> TokenCredential:
    """Build a TokenCredential from an ordered list of method names.

    Mirrors sara's ``AzureAd:AllowedAuthMethods`` pattern. The first
    credential in the chain that returns a token wins; subsequent ones are
    tried only when the previous raises ``CredentialUnavailableError``.

    Limits error messages to only the configured methods (unlike
    ``DefaultAzureCredential``, which tries seven providers and produces a
    long composite error).

    Args:
        methods: ordered list of method names. Supported values:
            ``"WorkloadIdentity"``, ``"AzureCli"`` and ``"ClientSecret"``.
        tenant_id: tenant id used by ``ClientSecret``.
        client_id: client id used by ``ClientSecret``.
        client_secret: client secret used by ``ClientSecret``.

    Returns:
        The single underlying credential when only one method is available in
        the current environment; otherwise a ``ChainedTokenCredential``
        preserving the given order.

    Raises:
        ValueError: if ``methods`` is empty, contains an unknown name, or none
            of the configured methods are available in the current environment.
    """
    if not methods:
        raise ValueError(
            "Auth methods list must not be empty. "
            f"Supported: {list(_SUPPORTED_METHODS)}"
        )

    unknown = [m for m in methods if m not in _SUPPORTED_METHODS]
    if unknown:
        raise ValueError(
            f"Unknown auth method(s): {unknown}. "
            f"Supported: {list(_SUPPORTED_METHODS)}"
        )

    factories: dict[str, Callable[[], Optional[TokenCredential]]] = {
        "WorkloadIdentity": _build_workload_identity,
        "AzureCli": _build_azure_cli,
        "ClientSecret": lambda: _build_client_secret(
            tenant_id, client_id, client_secret
        ),
    }

    credentials = [c for c in (factories[m]() for m in methods) if c]
    if not credentials:
        raise ValueError(
            f"None of the configured auth methods are available: {methods}. "
            f"WorkloadIdentity requires {list(_WI_REQUIRED_ENV_VARS)} env vars; "
            "ClientSecret requires tenant_id/client_id/client_secret arguments."
        )

    if len(credentials) == 1:
        return credentials[0]
    return ChainedTokenCredential(*credentials)
