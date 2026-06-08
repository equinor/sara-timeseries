from pathlib import Path

import pytest
from azure.identity import (
    AzureCliCredential,
    ChainedTokenCredential,
    ClientSecretCredential,
    WorkloadIdentityCredential,
)
from pytest import MonkeyPatch

from sara_timeseries.core.credentials import (
    _WI_REQUIRED_ENV_VARS,
    build_credential,
)


def _set_wi_env(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    """Pretend we're inside a WI-enabled pod."""
    token_file = tmp_path / "token"
    token_file.write_text("fake-token")
    monkeypatch.setenv("AZURE_TENANT_ID", "3aa4a235-b6e2-48d5-9195-7fcf05b459b0")
    monkeypatch.setenv("AZURE_CLIENT_ID", "dd7e115a-037e-4846-99c4-07561158a9cd")
    monkeypatch.setenv("AZURE_FEDERATED_TOKEN_FILE", str(token_file))


def _clear_wi_env(monkeypatch: MonkeyPatch) -> None:
    for v in _WI_REQUIRED_ENV_VARS:
        monkeypatch.delenv(v, raising=False)


def test_single_method_returns_underlying_credential(
    monkeypatch: MonkeyPatch,
) -> None:
    _clear_wi_env(monkeypatch)
    cred = build_credential(["AzureCli"])
    assert isinstance(cred, AzureCliCredential)


def test_multiple_methods_returns_chained_credential_in_order(
    monkeypatch: MonkeyPatch, tmp_path: Path
) -> None:
    _set_wi_env(monkeypatch, tmp_path)
    cred = build_credential(["WorkloadIdentity", "AzureCli"])
    assert isinstance(cred, ChainedTokenCredential)
    inner = cred.credentials  # type: ignore[attr-defined]
    assert isinstance(inner[0], WorkloadIdentityCredential)
    assert isinstance(inner[1], AzureCliCredential)


def test_workload_identity_skipped_outside_pod(monkeypatch: MonkeyPatch) -> None:
    """WI silently drops out of the chain when env vars are absent."""
    _clear_wi_env(monkeypatch)
    cred = build_credential(["WorkloadIdentity", "AzureCli"])
    assert isinstance(cred, AzureCliCredential)


def test_client_secret_method_returns_credential(monkeypatch: MonkeyPatch) -> None:
    _clear_wi_env(monkeypatch)
    cred = build_credential(
        ["ClientSecret"],
        tenant_id="tenant",
        client_id="client",
        client_secret="secret",
    )
    assert isinstance(cred, ClientSecretCredential)


def test_client_secret_skipped_when_secret_missing(
    monkeypatch: MonkeyPatch,
) -> None:
    _clear_wi_env(monkeypatch)
    cred = build_credential(
        ["ClientSecret", "AzureCli"],
        tenant_id="tenant",
        client_id="client",
        client_secret=None,
    )
    assert isinstance(cred, AzureCliCredential)


def test_three_method_chain_preserves_order(
    monkeypatch: MonkeyPatch, tmp_path: Path
) -> None:
    _set_wi_env(monkeypatch, tmp_path)
    cred = build_credential(
        ["WorkloadIdentity", "ClientSecret", "AzureCli"],
        tenant_id="tenant",
        client_id="client",
        client_secret="secret",
    )
    assert isinstance(cred, ChainedTokenCredential)
    inner = cred.credentials  # type: ignore[attr-defined]
    assert isinstance(inner[0], WorkloadIdentityCredential)
    assert isinstance(inner[1], ClientSecretCredential)
    assert isinstance(inner[2], AzureCliCredential)


def test_empty_methods_raises_value_error() -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        build_credential([])


def test_unknown_method_raises_value_error() -> None:
    with pytest.raises(ValueError, match="Unknown auth method"):
        build_credential(["ManagedIdentity"])


def test_unknown_method_error_lists_supported() -> None:
    with pytest.raises(ValueError, match="ClientSecret"):
        build_credential(["Bogus"])


def test_only_wi_with_no_env_raises_value_error(monkeypatch: MonkeyPatch) -> None:
    _clear_wi_env(monkeypatch)
    with pytest.raises(ValueError, match="None of the configured auth methods"):
        build_credential(["WorkloadIdentity"])


def test_only_client_secret_without_secret_raises_value_error(
    monkeypatch: MonkeyPatch,
) -> None:
    _clear_wi_env(monkeypatch)
    with pytest.raises(ValueError, match="None of the configured auth methods"):
        build_credential(
            ["ClientSecret"],
            tenant_id="tenant",
            client_id="client",
            client_secret=None,
        )
