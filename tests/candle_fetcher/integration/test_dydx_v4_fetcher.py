from typing import List
import pytest

from sir_utilities.date_time import string_to_datetime

from locast.candle.candle_utility import CandleUtility as cu
from locast.candle.dydx.dydx_resolution import DydxResolution
from locast.candle_fetcher.dydx.candle_fetcher.dydx_candle_fetcher import (
    DydxCandleFetcher,
)


# This test documents missing candles on dydx mainnet (!) backend.
# Trust me, you can look them up in their frontend - they are missing...


missing_candle_dates: List[str] = [
    "2024-07-25T06:53:00.000Z",
    "2024-10-03T14:13:00.000Z",
]


@pytest.mark.skip(reason="This is only to check if dYdX fixed their missing candles.")
@pytest.mark.parametrize("started_at", missing_candle_dates)
@pytest.mark.asyncio
async def test_missing_candles_on_mainnet(
    dydx_v4_candle_fetcher_mainnet: DydxCandleFetcher,
    started_at: str,
) -> None:
    # given
    res = DydxResolution.ONE_MINUTE
    fetcher = dydx_v4_candle_fetcher_mainnet
    start = string_to_datetime(started_at)
    end = cu.add_one_resolution(start, res)

    # when
    candles = await fetcher.fetch_candles(
        "ETH-USD",
        res,
        start,
        end,
    )

    # then - since backend is missing this specific candle
    assert candles == []
