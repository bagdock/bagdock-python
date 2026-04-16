"""Exception hierarchy for the Bagdock SDK."""

from __future__ import annotations

from typing import Any

import httpx


class BagdockError(Exception):
    """Base exception for all Bagdock errors."""


class AuthenticationError(BagdockError):
    """Raised when authentication fails or API key is missing."""


class BagdockApiError(BagdockError):
    """Raised when the Bagdock API returns an error response."""

    def __init__(
        self,
        message: str,
        *,
        status: int = 0,
        code: str = "unknown_error",
        request_id: str | None = None,
        response: httpx.Response | None = None,
    ) -> None:
        super().__init__(message)
        self.status = status
        self.code = code
        self.request_id = request_id
        self.response = response

    @classmethod
    def from_response(cls, response: httpx.Response) -> BagdockApiError:
        try:
            body: dict[str, Any] = response.json()
        except Exception:
            body = {}
        return cls(
            message=body.get("message", f"Request failed with status {response.status_code}"),
            status=response.status_code,
            code=body.get("code", "unknown_error"),
            request_id=body.get("request_id") or response.headers.get("x-request-id"),
            response=response,
        )


class RateLimitError(BagdockApiError):
    """Raised when the API rate limit is exceeded."""

    def __init__(self, response: httpx.Response) -> None:
        retry_after = response.headers.get("retry-after", "unknown")
        super().__init__(
            f"Rate limit exceeded. Retry after {retry_after}s",
            status=429,
            code="rate_limit_exceeded",
            response=response,
        )
        self.retry_after = retry_after
