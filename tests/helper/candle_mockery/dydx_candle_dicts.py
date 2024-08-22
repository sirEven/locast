from copy import copy
from typing import Any, Dict

from tests.helper.candle_mockery.base_values import copy_base_values


bv = copy_base_values()

dydx_v4_candle_dict: Dict[str, Any] = {
    "startedAt": bv["STARTED_AT"],
    "ticker": bv["TICKER"],
    "resolution": bv["RESOLUTION"],
    "low": bv["PRICE"],
    "high": bv["PRICE"],
    "open": bv["PRICE"],
    "close": bv["PRICE"],
    "baseTokenVolume": bv["BASE_TOKEN_VOLUME"],
    "usdVolume": bv["USD_VOLUME"],
    "trades": bv["TRADES"],
    "startingOpenInterest": bv["STARTING_OPEN_INTEREST"],
}


dydx_v3_candle_dict: Dict[str, Any] = {
    "startedAt": bv["STARTED_AT"],
    "market": bv["TICKER"],
    "resolution": bv["RESOLUTION"],
    "low": bv["PRICE"],
    "high": bv["PRICE"],
    "open": bv["PRICE"],
    "close": bv["PRICE"],
    "baseTokenVolume": bv["BASE_TOKEN_VOLUME"],
    "usdVolume": bv["USD_VOLUME"],
    "trades": bv["TRADES"],
    "startingOpenInterest": bv["STARTING_OPEN_INTEREST"],
}


def copy_dydx_v4_base_candle_dict() -> Dict[str, Any]:
    return copy(dydx_v4_candle_dict)


def copy_dydx_v3_base_candle_dict() -> Dict[str, Any]:
    return copy(dydx_v3_candle_dict)
