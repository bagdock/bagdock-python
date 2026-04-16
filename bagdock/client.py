"""HTTP client with sync and async interfaces."""

from __future__ import annotations

import os
from typing import Any

import httpx

from bagdock.exceptions import BagdockApiError, AuthenticationError, RateLimitError
from bagdock.oauth import TokenManager, AsyncTokenManager, OAuthEndpoints
from bagdock.resources.operator import OperatorResource
from bagdock.resources.marketplace import MarketplaceResource
from bagdock.resources.loyalty import LoyaltyResource

DEFAULT_BASE_URL = "https://api.bagdock.com/api/v1"
DEFAULT_TIMEOUT = 30.0
DEFAULT_MAX_RETRIES = 3
MAX_RETRY_CAP = 5


class _BaseClient:
    def __init__(
        self,
        api_key: str | None = None,
        access_token: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
        scopes: list[str] | None = None,
        oauth_endpoints: OAuthEndpoints | None = None,
        base_url: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ) -> None:
        self.base_url = (base_url or DEFAULT_BASE_URL).rstrip("/")
        self.timeout = timeout
        self.max_retries = min(max_retries, MAX_RETRY_CAP)

        resolved_key = api_key or os.environ.get("BAGDOCK_API_KEY")
        if resolved_key:
            self._auth_mode = "api_key"
            self._static_token = resolved_key
            self._token_manager: TokenManager | None = None
            self._async_token_manager: AsyncTokenManager | None = None
        elif access_token:
            self._auth_mode = "access_token"
            self._static_token = access_token
            self._token_manager = None
            self._async_token_manager = None
        elif client_id and client_secret:
            self._auth_mode = "client_credentials"
            self._static_token = None
            self._token_manager = TokenManager(
                client_id=client_id,
                client_secret=client_secret,
                scopes=scopes,
                endpoints=oauth_endpoints,
            )
            self._async_token_manager = AsyncTokenManager(
                client_id=client_id,
                client_secret=client_secret,
                scopes=scopes,
                endpoints=oauth_endpoints,
            )
        else:
            raise AuthenticationError(
                "Provide one of: api_key, access_token, or client_id + client_secret."
            )

    def _get_token_sync(self) -> str:
        if self._static_token:
            return self._static_token
        assert self._token_manager is not None
        return self._token_manager.get_token()

    async def _get_token_async(self) -> str:
        if self._static_token:
            return self._static_token
        assert self._async_token_manager is not None
        return await self._async_token_manager.get_token()

    def _headers(self, token: str) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "bagdock-python/0.1.0",
        }


class Bagdock(_BaseClient):
    """Synchronous Bagdock API client."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        token = self._get_token_sync()
        transport = httpx.HTTPTransport(retries=self.max_retries)
        self._http = httpx.Client(
            base_url=self.base_url,
            headers=self._headers(token),
            timeout=self.timeout,
            transport=transport,
        )
        self.operator = OperatorResource(self._http)
        self.marketplace = MarketplaceResource(self._http)
        self.loyalty = LoyaltyResource(self._http)

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> Bagdock:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def request(
        self,
        method: str,
        path: str,
        *,
        json: Any = None,
        params: dict[str, Any] | None = None,
    ) -> Any:
        if self._token_manager:
            token = self._get_token_sync()
            self._http.headers["Authorization"] = f"Bearer {token}"
        response = self._http.request(method, path, json=json, params=params)
        if response.status_code == 401 and self._token_manager:
            self._token_manager.invalidate()
            token = self._get_token_sync()
            self._http.headers["Authorization"] = f"Bearer {token}"
            response = self._http.request(method, path, json=json, params=params)
        return _handle_response(response)


class AsyncBagdock(_BaseClient):
    """Asynchronous Bagdock API client."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        transport = httpx.AsyncHTTPTransport(retries=self.max_retries)
        self._http = httpx.AsyncClient(
            base_url=self.base_url,
            headers=self._headers(self._static_token or "pending"),
            timeout=self.timeout,
            transport=transport,
        )
        self.operator = OperatorResource(self._http)
        self.marketplace = MarketplaceResource(self._http)
        self.loyalty = LoyaltyResource(self._http)

    async def close(self) -> None:
        await self._http.aclose()

    async def __aenter__(self) -> AsyncBagdock:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    async def request(
        self,
        method: str,
        path: str,
        *,
        json: Any = None,
        params: dict[str, Any] | None = None,
    ) -> Any:
        token = await self._get_token_async()
        self._http.headers["Authorization"] = f"Bearer {token}"
        response = await self._http.request(method, path, json=json, params=params)
        if response.status_code == 401 and self._async_token_manager:
            self._async_token_manager.invalidate()
            token = await self._get_token_async()
            self._http.headers["Authorization"] = f"Bearer {token}"
            response = await self._http.request(method, path, json=json, params=params)
        return _handle_response(response)


def _handle_response(response: httpx.Response) -> Any:
    if response.status_code == 204:
        return None
    if response.status_code == 429:
        raise RateLimitError(response=response)
    if response.status_code >= 400:
        raise BagdockApiError.from_response(response)
    return response.json()
