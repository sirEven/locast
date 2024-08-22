from copy import copy
from typing import Any, Dict


STARTED_AT = "2024-05-06T17:24:00.000Z"
TICKER = "LINK-USD"
RESOLUTION = "1MIN"
PRICE = "14.688"
BASE_TOKEN_VOLUME = "0"
USD_VOLUME = "0"
TRADES = 0
STARTING_OPEN_INTEREST = "11132"

dydx_v4_candle_dict: Dict[str, Any] = {
    "startedAt": STARTED_AT,
    "ticker": TICKER,
    "resolution": RESOLUTION,
    "low": PRICE,
    "high": PRICE,
    "open": PRICE,
    "close": PRICE,
    "baseTokenVolume": BASE_TOKEN_VOLUME,
    "usdVolume": USD_VOLUME,
    "trades": TRADES,
    "startingOpenInterest": STARTING_OPEN_INTEREST,
}


dydx_v3_candle_dict: Dict[str, Any] = {
    "startedAt": STARTED_AT,
    "market": TICKER,
    "resolution": RESOLUTION,
    "low": PRICE,
    "high": PRICE,
    "open": PRICE,
    "close": PRICE,
    "baseTokenVolume": BASE_TOKEN_VOLUME,
    "usdVolume": USD_VOLUME,
    "trades": TRADES,
    "startingOpenInterest": STARTING_OPEN_INTEREST,
}


def copy_dydx_v4_base_candle_dict() -> Dict[str, Any]:
    return copy(dydx_v4_candle_dict)


def copy_dydx_v3_base_candle_dict() -> Dict[str, Any]:
    return copy(dydx_v3_candle_dict)
