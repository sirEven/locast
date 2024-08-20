from datetime import timedelta
import pytest

from sir_utilities.date_time import now_utc_iso


from locast.candle.candle_utility import CandleUtility as cu
from locast.candle.dydx.dydx_resolution import DydxResolution
from locast.candle_fetcher.dydx.candle_fetcher.dydx_v4_candle_fetcher import (
    DydxV4CandleFetcher,
)
from sir_utilities.date_time import string_to_datetime


# TODO: Paramaterize with edge case amounts (0, 1, 2, 10, 100, 1000, 10000) as well as resolutions (all of them)
@pytest.mark.asyncio
async def test_v4_fetch_600_historic_candles_testnet(
    dydx_v4_candle_fetcher_testnet: DydxV4CandleFetcher,
) -> None:
    # given
    fetcher = dydx_v4_candle_fetcher_testnet
    res = DydxResolution.ONE_MINUTE
    start = string_to_datetime("2024-04-01T00:00:00.000Z")
    end = string_to_datetime("2024-04-01T10:00:00.000Z")

    # when
    candles = await fetcher.fetch_candles(
        "ETH-USD",
        res.notation,
        start,
        end,
    )

    # then
    assert len(candles) == 600
    assert candles[-1].started_at == start
    assert candles[0].started_at == end - timedelta(seconds=res.seconds)


@pytest.mark.asyncio
async def test_v4_fetch_600_historic_candles_mainnet(
    dydx_v4_candle_fetcher_mainnet: DydxV4CandleFetcher,
) -> None:
    # given
    fetcher = dydx_v4_candle_fetcher_mainnet
    res = DydxResolution.ONE_MINUTE
    start = string_to_datetime("2024-06-01T00:00:00.000Z")
    end = string_to_datetime("2024-06-01T10:00:00.000Z")

    # when
    candles = await fetcher.fetch_candles(
        "ETH-USD",
        res.notation,
        start,
        end,
    )

    # then
    assert len(candles) == 600
    assert candles[-1].started_at == start
    assert candles[0].started_at == end - timedelta(seconds=res.seconds)


# TODO: Paramaterize with edge case amounts (0, 1, 2, 10, 100, 1000, 10000) as well as resolutions (all of them)
@pytest.mark.asyncio
async def test_v4_fetch_cluster_is_up_to_date(
    dydx_v4_candle_fetcher_mainnet: DydxV4CandleFetcher,
) -> None:
    # given
    fetcher = dydx_v4_candle_fetcher_mainnet
    res = DydxResolution.ONE_MINUTE
    amount_back = 24000
    now_rounded = cu.norm_date(now_utc_iso(), res.seconds)
    start_date = now_rounded - timedelta(seconds=res.seconds * amount_back)

    candles = await fetcher.fetch_candles_up_to_now(
        "ETH-USD",
        res.notation,
        start_date,
    )

    # then
    cu.assert_candle_unity(candles)
    cu.assert_chronologic_order(candles)
    assert cu.is_newest_valid_candle(candles[0])
    assert len(candles) >= amount_back


# NOTE: This test exists only to see, wether the backend is being maintained to sometime include this candle again or not (which I'm sure will not happen).
# Order violated from Candles None (2024-07-25 06:52:00+00:00) to None (2024-07-25 06:54:00+00:00)
# Meaning: The (mainnet!) backend is actually missing one candle (which startedAt 2024-07-25 06:53:00+00:00)
@pytest.mark.asyncio
async def test_candle_error_at_2024_07_25_06_52(
    dydx_v4_candle_fetcher_mainnet: DydxV4CandleFetcher,
) -> None:
    # given
    res = DydxResolution.ONE_MINUTE
    fetcher = dydx_v4_candle_fetcher_mainnet
    start = string_to_datetime("2024-07-25T06:53:00.000Z")
    end = string_to_datetime("2024-07-25T06:54:00.000Z")

    # when
    candles = await fetcher.fetch_candles(
        "ETH-USD",
        res.notation,
        start,
        end,
    )

    # then - since backend is missing this specific candle
    assert candles == []
