import pytest

from sir_utilities.date_time import string_to_datetime

from locast.candle.dydx.dydx_resolution import DydxResolution
from locast.candle_fetcher.dydx.candle_fetcher.dydx_candle_fetcher import (
    DydxCandleFetcher,
)


# This test exists only to see, wether the v4 backend is being maintained to sometime include this candle again or not (which I'm sure will not happen).
# Order violated from Candles None (2024-07-25 06:52:00+00:00) to None (2024-07-25 06:54:00+00:00)
# Meaning: The (mainnet!) backend is actually missing one candle (which startedAt 2024-07-25 06:53:00+00:00)
@pytest.mark.skip(reason="This is only to check if dYdX fixed their missing candle.")
@pytest.mark.asyncio
async def test_candle_error_at_2024_07_25_06_52(
    dydx_v4_candle_fetcher_mainnet: DydxCandleFetcher,
) -> None:
    # given
    res = DydxResolution.ONE_MINUTE
    fetcher = dydx_v4_candle_fetcher_mainnet
    start = string_to_datetime("2024-07-25T06:53:00.000Z")
    end = string_to_datetime("2024-07-25T06:54:00.000Z")

    # when
    candles = await fetcher.fetch_candles(
        "ETH-USD",
        res,
        start,
        end,
    )

    # then - since backend is missing this specific candle
    assert candles == []
