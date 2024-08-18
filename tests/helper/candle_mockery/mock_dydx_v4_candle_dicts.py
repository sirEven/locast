from datetime import datetime, timedelta
from typing import Any, Dict, List

from sir_utilities.date_time import datetime_to_string, string_to_datetime

from locast.candle.candle_utility import CandleUtility as cu
from locast.candle.dydx.dydx_resolution import DydxResolution


base_dict: Dict[str, Any] = {
    "startedAt": "2024-05-06T17:24:00.000Z",
    "ticker": "LINK-USD",
    "resolution": "1MIN",
    "low": "14.688",
    "high": "14.688",
    "open": "14.688",
    "close": "14.688",
    "baseTokenVolume": "0",
    "usdVolume": "0",
    "trades": 0,
    "startingOpenInterest": "11132",
}


def replace_date(
    candle_dict: Dict[str, Any],
    date: datetime,
) -> Dict[str, Any]:
    date_rounded = date.replace(microsecond=0, second=0)
    candle_dict["startedAt"] = datetime_to_string(date_rounded)
    return candle_dict


def subtract_resolution(date_str: str, resolution: str) -> datetime:
    date = string_to_datetime(date_str)
    res_sec = DydxResolution.notation_to_seconds(resolution)
    return date - timedelta(seconds=res_sec)


def mock_dydx_v4_candle_dict_batch(
    resolution: str,
    market: str,
    from_iso: str,
    to_iso: str,
    batch_size: int = 1000,
) -> List[Dict[str, Any]]:
    """
    Generates mocked price candles for a given market, resolution, and time range.

    Args:
        market (str): The market for which to mock candles.
        resolution (str): The resolution of the candles.
        from_iso (Optional[str], optional): The start date of the candle range in ISO format. Defaults to None.
        to_iso (Optional[str], optional): The end date of the candle range in ISO format. Defaults to None.
        limit (Optional[int], optional): The maximum number of candles to retrieve. Defaults to None.

    Returns:
        Dict[str, Any]: A dictionary containing a list of candle dictionaries.

    Raises:
        AssertionError: If to_iso or from_iso is not provided when mocking candles.

    Note:
        1) Before the first iteration we always add the first candle to the (then empty) batch in order to
        simplify the index based algorithm and prevent duplicates (at the end of one batch and the beginning of the next).
        While doing so we also modify certain attributes of that first batch candle, to correspond to the input resolution,
        market and date range.
        2) Specifically we subtract one resolution from the date, because the very first candle (which is the most
        recent one chronologically aka the newest one) will only reach to the to_iso date from its startedAt date which
        is one resolution earlier.
        3) Because of this strategy (adding the first candle by hand) we need to subtract 1 from the range input in our
        for loop, since we want every batch to be either 1000 candles wide
        or less, if the provided range entails less.
        4) V4 MAINNET backend responds in batch sizes of 1000 candle dicts,
        5) V4 TESTNET backend responds in batch sizes of 100 candle dicts.
    """

    temp_candle = base_dict
    temp_candle = replace_date(
        temp_candle,
        subtract_resolution(to_iso, resolution),
    )

    temp_candle["resolution"] = resolution
    temp_candle["ticker"] = market
    candle_dicts_batch: List[Dict[str, Any]] = [temp_candle]

    amount = min(
        cu.amount_of_candles_in_range(
            string_to_datetime(from_iso),
            string_to_datetime(to_iso),
            DydxResolution.notation_to_seconds(resolution),
        ),
        batch_size,
    )

    for i in range(amount - 1):
        new_date = subtract_resolution(
            candle_dicts_batch[i]["startedAt"],
            candle_dicts_batch[i]["resolution"],
        )
        candle_dict = replace_date(candle_dicts_batch[i].copy(), new_date)
        candle_dicts_batch.append(candle_dict)
    return candle_dicts_batch
