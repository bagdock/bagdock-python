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

## Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `api_key` | `str` | `BAGDOCK_API_KEY` env | **Required.** Your Bagdock API key |
| `base_url` | `str` | `https://api.bagdock.com/api/v1` | API base URL |
| `timeout` | `float` | `30.0` | Request timeout in seconds |
| `max_retries` | `int` | `2` | Max retry attempts for transient errors |

## License

MIT — see [LICENSE](LICENSE)
