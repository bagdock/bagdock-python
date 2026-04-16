```
  ----++                                ----++                    ---+++     
  ---+++                                ---++                     ---++      
 ----+---     -----     ---------  --------++ ------     -----   ----++----- 
 ---------+ --------++----------++--------+++--------+ --------++---++---++++
 ---+++---++ ++++---++---+++---++---+++---++---+++---++---++---++------++++  
----++ ---++--------++---++----++---++ ---++---++ ---+---++     -------++    
----+----+---+++---++---++----++---++----++---++---+++--++ --------+---++   
---------++--------+++--------+++--------++ -------+++ -------++---++----++  
 +++++++++   +++++++++- +++---++   ++++++++    ++++++    ++++++  ++++  ++++  
                     --------+++                                             
                       +++++++                                               
```

# bagdock

The official Python SDK for the Bagdock API — manage facilities, contacts, tenancies, invoices, marketplace listings, and loyalty programs with sync and async clients.

[![PyPI version](https://img.shields.io/pypi/v/bagdock.svg)](https://pypi.org/project/bagdock/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## Install

```bash
pip install bagdock
```

```bash
poetry add bagdock
```

```bash
uv add bagdock
```

## Quick start

```python
from bagdock import Bagdock

client = Bagdock(api_key="sk_live_...")

# List operator facilities
facilities = client.operator.facilities.list(page=1, per_page=20)

# Create a contact
contact = client.operator.contacts.create({
    "email": "jane@example.com",
    "first_name": "Jane",
    "last_name": "Doe",
})

# Search marketplace
locations = client.marketplace.search(city="London", size="medium")
```

## Async usage

```python
from bagdock import AsyncBagdock

async with AsyncBagdock(api_key="sk_live_...") as client:
    facilities = await client.operator.facilities.list()
```

## API reference

### `client.operator`

| Method | Description |
|--------|-------------|
| `facilities.list(**params)` | List facilities |
| `facilities.get(id)` | Get a facility |
| `facilities.create(data)` | Create a facility |
| `contacts.list(**params)` | List contacts |
| `contacts.create(data)` | Create a contact |
| `listings.list(**params)` | List listings |
| `tenancies.list(**params)` | List tenancies |
| `units.list(**params)` | List units |
| `invoices.list(**params)` | List invoices |
| `payments.list(**params)` | List payments |

### `client.marketplace`

| Method | Description |
|--------|-------------|
| `search(**params)` | Search marketplace locations |
| `get_listing(id)` | Get a listing |
| `create_rental(data)` | Create a rental |
| `get_rental(id)` | Get a rental |
| `check_availability(**params)` | Check availability |

### `client.loyalty`

| Method | Description |
|--------|-------------|
| `create_member(data)` | Create a loyalty member |
| `get_member(id)` | Get a member |
| `get_balance(member_id)` | Get points balance |
| `award_points(data)` | Award points |
| `redeem_points(data)` | Redeem points |
| `list_rewards(**params)` | List rewards |

## Error handling

```python
from bagdock import Bagdock, BagdockApiError, RateLimitError

try:
    client.operator.contacts.get("con_nonexistent")
except RateLimitError as e:
    print(f"Rate limited — retry after {e.retry_after}s")
except BagdockApiError as e:
    print(f"API error {e.status}: {e.code} — {e}")
```

## Authentication

The SDK supports three authentication modes: API keys, OAuth access tokens, and OAuth2 client credentials.

### API key

```python
from bagdock import Bagdock

client = Bagdock(api_key="sk_live_...")
# or set BAGDOCK_API_KEY env var
client = Bagdock()
```

### OAuth access token

```python
client = Bagdock(access_token="eyJhbGciOiJSUzI1NiIs...")
```

### Client credentials

```python
client = Bagdock(
    client_id="oac_your_client_id",
    client_secret="bdok_secret_your_secret",
    scopes=["facilities:read", "contacts:read"],
)
```

### OAuth2 helpers

These helpers support authorization code (with PKCE) and device code flows. They are also useful for **connect webviews** in external integrations—such as access control, security, and insurance—where you need to obtain tokens without embedding long-lived secrets in user-facing code.

```python
from bagdock import generate_pkce, build_authorize_url, exchange_code, refresh_token, device_authorize, poll_device_token

pkce = generate_pkce()
url = build_authorize_url(
    client_id="oac_your_client_id",
    redirect_uri="https://your-app.com/callback",
    code_challenge=pkce.code_challenge,
    scope="openid contacts:read facilities:read",
)

tokens = exchange_code(
    client_id="oac_your_client_id",
    code="authorization_code_from_callback",
    redirect_uri="https://your-app.com/callback",
    code_verifier=pkce.code_verifier,
)

device = device_authorize(client_id="bagdock-cli", scope="developer:read developer:write")
print(f"Open {device.verification_uri} and enter: {device.user_code}")
device_tokens = poll_device_token(client_id="bagdock-cli", device_code=device.device_code)
```

## Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `api_key` | `str` | `BAGDOCK_API_KEY` env | Your Bagdock API key (omit if using `access_token` or client credentials) |
| `access_token` | `str` | — | OAuth access token (Bearer) |
| `client_id` | `str` | — | OAuth2 client ID (with `client_secret` and `scopes` for client credentials) |
| `client_secret` | `str` | — | OAuth2 client secret |
| `scopes` | `list[str]` | — | OAuth2 scopes for client credentials |
| `base_url` | `str` | `https://api.bagdock.com/api/v1` | API base URL |
| `timeout` | `float` | `30.0` | Request timeout in seconds |
| `max_retries` | `int` | `3` | Max retry attempts for transient errors (capped at 5) |

## Documentation

- [Full documentation](https://bagdock.com/docs)
- [Python SDK quickstart](https://bagdock.com/docs/sdks/python)
- [API reference](https://bagdock.com/docs/api)
- [OAuth2 / OIDC guide](https://bagdock.com/docs/auth/oauth2)

## License

MIT — see [LICENSE](LICENSE)
