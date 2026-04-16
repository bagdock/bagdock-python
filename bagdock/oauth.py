"""OAuth2 / OIDC helpers for the Bagdock SDK.

Provides PKCE utilities, authorization URL building, token exchange,
refresh, revocation, introspection, and device-code flow support.
"""

from __future__ import annotations

import base64
import hashlib
import os
import time
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urlencode

import httpx

DEFAULT_ISSUER = "https://api.bagdock.com"
DEVICE_CODE_GRANT_TYPE = "urn:ietf:params:oauth:grant-type:device_code"


# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------

@dataclass
class OAuthEndpoints:
    issuer: str = DEFAULT_ISSUER
    token_endpoint: str | None = None
    authorize_endpoint: str | None = None
    device_authorize_endpoint: str | None = None
    revoke_endpoint: str | None = None
    introspect_endpoint: str | None = None
    userinfo_endpoint: str | None = None

    def _resolve(self, suffix: str, override: str | None) -> str:
        if override:
            return override
        return f"{self.issuer.rstrip('/')}{suffix}"

    @property
    def token(self) -> str:
        return self._resolve("/oauth2/token", self.token_endpoint)

    @property
    def authorize(self) -> str:
        return self._resolve("/oauth2/authorize", self.authorize_endpoint)

    @property
    def device_authorize(self) -> str:
        return self._resolve("/oauth2/device/authorize", self.device_authorize_endpoint)

    @property
    def revoke(self) -> str:
        return self._resolve("/oauth2/token/revoke", self.revoke_endpoint)

    @property
    def introspect(self) -> str:
        return self._resolve("/oauth2/token/introspect", self.introspect_endpoint)

    @property
    def userinfo(self) -> str:
        return self._resolve("/oauth2/userinfo", self.userinfo_endpoint)


@dataclass
class PKCEPair:
    code_verifier: str
    code_challenge: str


@dataclass
class TokenResponse:
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str | None = None
    id_token: str | None = None
    scope: str | None = None


@dataclass
class DeviceAuthResponse:
    device_code: str
    user_code: str
    verification_uri: str
    expires_in: int
    interval: int
    verification_uri_complete: str | None = None


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class OAuthError(Exception):
    def __init__(self, message: str, code: str = "oauth_error", status: int = 0) -> None:
        super().__init__(message)
        self.code = code
        self.status = status


# ---------------------------------------------------------------------------
# PKCE helpers (RFC 7636)
# ---------------------------------------------------------------------------

def generate_pkce() -> PKCEPair:
    verifier_bytes = os.urandom(32)
    code_verifier = base64.urlsafe_b64encode(verifier_bytes).rstrip(b"=").decode("ascii")
    digest = hashlib.sha256(code_verifier.encode("ascii")).digest()
    code_challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    return PKCEPair(code_verifier=code_verifier, code_challenge=code_challenge)


# ---------------------------------------------------------------------------
# Authorize URL
# ---------------------------------------------------------------------------

def build_authorize_url(
    *,
    client_id: str,
    redirect_uri: str,
    code_challenge: str,
    scope: str | None = None,
    state: str | None = None,
    code_challenge_method: str = "S256",
    endpoints: OAuthEndpoints | None = None,
) -> str:
    ep = endpoints or OAuthEndpoints()
    params: dict[str, str] = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "code_challenge": code_challenge,
        "code_challenge_method": code_challenge_method,
    }
    if scope:
        params["scope"] = scope
    if state:
        params["state"] = state
    return f"{ep.authorize}?{urlencode(params)}"


# ---------------------------------------------------------------------------
# Token helpers
# ---------------------------------------------------------------------------

def _post_form(url: str, data: dict[str, str]) -> dict[str, Any]:
    response = httpx.post(url, data=data)
    body = response.json()
    if response.status_code >= 400:
        raise OAuthError(
            body.get("error_description", body.get("error", f"HTTP {response.status_code}")),
            code=body.get("error", "oauth_error"),
            status=response.status_code,
        )
    return body


async def _async_post_form(url: str, data: dict[str, str]) -> dict[str, Any]:
    async with httpx.AsyncClient() as client:
        response = await client.post(url, data=data)
    body = response.json()
    if response.status_code >= 400:
        raise OAuthError(
            body.get("error_description", body.get("error", f"HTTP {response.status_code}")),
            code=body.get("error", "oauth_error"),
            status=response.status_code,
        )
    return body


def _to_token_response(data: dict[str, Any]) -> TokenResponse:
    return TokenResponse(
        access_token=data["access_token"],
        token_type=data["token_type"],
        expires_in=data["expires_in"],
        refresh_token=data.get("refresh_token"),
        id_token=data.get("id_token"),
        scope=data.get("scope"),
    )


def exchange_code(
    *,
    client_id: str,
    code: str,
    redirect_uri: str,
    code_verifier: str,
    client_secret: str | None = None,
    endpoints: OAuthEndpoints | None = None,
) -> TokenResponse:
    ep = endpoints or OAuthEndpoints()
    data: dict[str, str] = {
        "grant_type": "authorization_code",
        "client_id": client_id,
        "code": code,
        "redirect_uri": redirect_uri,
        "code_verifier": code_verifier,
    }
    if client_secret:
        data["client_secret"] = client_secret
    return _to_token_response(_post_form(ep.token, data))


def refresh_token(
    *,
    client_id: str,
    refresh_token_value: str,
    client_secret: str | None = None,
    endpoints: OAuthEndpoints | None = None,
) -> TokenResponse:
    ep = endpoints or OAuthEndpoints()
    data: dict[str, str] = {
        "grant_type": "refresh_token",
        "client_id": client_id,
        "refresh_token": refresh_token_value,
    }
    if client_secret:
        data["client_secret"] = client_secret
    return _to_token_response(_post_form(ep.token, data))


def revoke_token(
    *,
    token: str,
    token_type_hint: str | None = None,
    client_id: str | None = None,
    client_secret: str | None = None,
    endpoints: OAuthEndpoints | None = None,
) -> None:
    ep = endpoints or OAuthEndpoints()
    data: dict[str, str] = {"token": token}
    if token_type_hint:
        data["token_type_hint"] = token_type_hint
    if client_id:
        data["client_id"] = client_id
    if client_secret:
        data["client_secret"] = client_secret
    response = httpx.post(ep.revoke, data=data)
    if response.status_code >= 400:
        body = response.json()
        raise OAuthError(
            body.get("error_description", "Revocation failed"),
            code=body.get("error", "revocation_error"),
            status=response.status_code,
        )


def introspect_token(
    *,
    token: str,
    token_type_hint: str | None = None,
    endpoints: OAuthEndpoints | None = None,
) -> dict[str, Any]:
    ep = endpoints or OAuthEndpoints()
    data: dict[str, str] = {"token": token}
    if token_type_hint:
        data["token_type_hint"] = token_type_hint
    return _post_form(ep.introspect, data)


def get_userinfo(
    access_token: str,
    endpoints: OAuthEndpoints | None = None,
) -> dict[str, Any]:
    ep = endpoints or OAuthEndpoints()
    response = httpx.get(ep.userinfo, headers={"Authorization": f"Bearer {access_token}"})
    if response.status_code >= 400:
        raise OAuthError("Failed to fetch userinfo", "userinfo_error", response.status_code)
    return response.json()


# ---------------------------------------------------------------------------
# Device Authorization (RFC 8628)
# ---------------------------------------------------------------------------

def device_authorize(
    *,
    client_id: str,
    scope: str | None = None,
    endpoints: OAuthEndpoints | None = None,
) -> DeviceAuthResponse:
    ep = endpoints or OAuthEndpoints()
    data: dict[str, str] = {"client_id": client_id}
    if scope:
        data["scope"] = scope
    body = _post_form(ep.device_authorize, data)
    return DeviceAuthResponse(
        device_code=body["device_code"],
        user_code=body["user_code"],
        verification_uri=body["verification_uri"],
        expires_in=body["expires_in"],
        interval=body["interval"],
        verification_uri_complete=body.get("verification_uri_complete"),
    )


def poll_device_token(
    *,
    client_id: str,
    device_code: str,
    interval: int = 5,
    timeout: int = 600,
    client_secret: str | None = None,
    endpoints: OAuthEndpoints | None = None,
) -> TokenResponse:
    ep = endpoints or OAuthEndpoints()
    deadline = time.monotonic() + timeout
    poll_interval = interval

    while time.monotonic() < deadline:
        time.sleep(poll_interval)
        data: dict[str, str] = {
            "grant_type": DEVICE_CODE_GRANT_TYPE,
            "client_id": client_id,
            "device_code": device_code,
        }
        if client_secret:
            data["client_secret"] = client_secret
        try:
            return _to_token_response(_post_form(ep.token, data))
        except OAuthError as e:
            if e.code == "authorization_pending":
                continue
            if e.code == "slow_down":
                poll_interval += 5
                continue
            raise

    raise OAuthError("Device authorization timed out", "expired_token", 408)


# ---------------------------------------------------------------------------
# Token manager for client credentials (used internally by SDK client)
# ---------------------------------------------------------------------------

class TokenManager:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        scopes: list[str] | None = None,
        endpoints: OAuthEndpoints | None = None,
    ) -> None:
        self._client_id = client_id
        self._client_secret = client_secret
        self._scopes = scopes
        self._endpoints = endpoints or OAuthEndpoints()
        self._access_token: str | None = None
        self._expires_at: float = 0

    def get_token(self) -> str:
        if self._access_token and time.monotonic() < self._expires_at:
            return self._access_token
        return self._fetch_token()

    def invalidate(self) -> None:
        self._access_token = None
        self._expires_at = 0

    def _fetch_token(self) -> str:
        data: dict[str, str] = {
            "grant_type": "client_credentials",
            "client_id": self._client_id,
            "client_secret": self._client_secret,
        }
        if self._scopes:
            data["scope"] = " ".join(self._scopes)
        body = _post_form(self._endpoints.token, data)
        self._access_token = body["access_token"]
        self._expires_at = time.monotonic() + body["expires_in"] - 60
        return self._access_token  # type: ignore[return-value]


class AsyncTokenManager:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        scopes: list[str] | None = None,
        endpoints: OAuthEndpoints | None = None,
    ) -> None:
        self._client_id = client_id
        self._client_secret = client_secret
        self._scopes = scopes
        self._endpoints = endpoints or OAuthEndpoints()
        self._access_token: str | None = None
        self._expires_at: float = 0

    async def get_token(self) -> str:
        if self._access_token and time.monotonic() < self._expires_at:
            return self._access_token
        return await self._fetch_token()

    def invalidate(self) -> None:
        self._access_token = None
        self._expires_at = 0

    async def _fetch_token(self) -> str:
        data: dict[str, str] = {
            "grant_type": "client_credentials",
            "client_id": self._client_id,
            "client_secret": self._client_secret,
        }
        if self._scopes:
            data["scope"] = " ".join(self._scopes)
        body = await _async_post_form(self._endpoints.token, data)
        self._access_token = body["access_token"]
        self._expires_at = time.monotonic() + body["expires_in"] - 60
        return self._access_token  # type: ignore[return-value]
