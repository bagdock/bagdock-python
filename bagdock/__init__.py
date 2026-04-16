"""Official Bagdock API client for Python."""

from bagdock.client import Bagdock, AsyncBagdock
from bagdock.exceptions import BagdockError, BagdockApiError, AuthenticationError, RateLimitError
from bagdock.oauth import (
    generate_pkce,
    build_authorize_url,
    exchange_code,
    refresh_token,
    revoke_token,
    introspect_token,
    get_userinfo,
    device_authorize,
    poll_device_token,
    OAuthError,
    OAuthEndpoints,
    PKCEPair,
    TokenResponse,
    DeviceAuthResponse,
)

__version__ = "0.1.0"
__all__ = [
    "Bagdock",
    "AsyncBagdock",
    "BagdockError",
    "BagdockApiError",
    "AuthenticationError",
    "RateLimitError",
    "generate_pkce",
    "build_authorize_url",
    "exchange_code",
    "refresh_token",
    "revoke_token",
    "introspect_token",
    "get_userinfo",
    "device_authorize",
    "poll_device_token",
    "OAuthError",
    "OAuthEndpoints",
    "PKCEPair",
    "TokenResponse",
    "DeviceAuthResponse",
]
