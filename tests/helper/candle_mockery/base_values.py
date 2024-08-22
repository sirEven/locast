from copy import copy
from typing import Any, Dict


base_values = {
    "STARTED_AT": "2024-05-06T17:24:00.000Z",
    "TICKER": "LINK-USD",
    "RESOLUTION": "1MIN",
    "PRICE": "14.688",
    "BASE_TOKEN_VOLUME": "0",
    "USD_VOLUME": "0",
    "TRADES": 0,
    "STARTING_OPEN_INTEREST": "11132",
}


def copy_base_values() -> Dict[str, Any]:
    return copy(base_values)
