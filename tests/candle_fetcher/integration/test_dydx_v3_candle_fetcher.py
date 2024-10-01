from datetime import timedelta
import pytest

from sir_utilities.date_time import now_utc_iso, string_to_datetime

from locast.candle.candle_utility import CandleUtility as cu
from locast.candle.dydx.dydx_resolution import DydxResolution
from locast.candle.resolution import ResolutionDetail
from locast.candle_fetcher.dydx.candle_fetcher.dydx_v3_candle_fetcher import (
    DydxV3CandleFetcher,
)

from tests.helper.parametrization.list_of_amounts import amounts
from tests.helper.parametrization.list_of_resolution_details import resolutions

resolutions_reduced = resolutions[:-2]  # Backend too young still


@pytest.mark.parametrize("resolution", resolutions_reduced)
@pytest.mark.asyncio
async def test_v3_fetch_range_of_candles_testnet(
    dydx_v3_candle_fetcher_testnet: DydxV3CandleFetcher,
    resolution: ResolutionDetail,
) -> None:
    # given
    fetcher = dydx_v3_candle_fetcher_testnet
    res = resolution
    start = string_to_datetime("2024-04-01T00:00:00.000Z")
    end = string_to_datetime("2024-04-01T10:00:00.000Z")

    # when
    candles = await fetcher.fetch_candles(
        "ETH-USD",
        res,
        start,
        end,
    )

    # then
    amount = cu.amount_of_candles_in_range(start, end, res)
    assert len(candles) == amount
    assert candles[-1].started_at == start
    assert candles[0].started_at == end - timedelta(seconds=res.seconds)


@pytest.mark.parametrize("resolution", resolutions_reduced)
@pytest.mark.asyncio
async def test_v3_fetch_range_of_candles_mainnet(
    dydx_v3_candle_fetcher_mainnet: DydxV3CandleFetcher,
    resolution: ResolutionDetail,
) -> None:
    # given
    fetcher = dydx_v3_candle_fetcher_mainnet
    res = resolution
    start = string_to_datetime("2024-06-01T00:00:00.000Z")
    end = string_to_datetime("2024-06-01T10:00:00.000Z")

    # when
    candles = await fetcher.fetch_candles(
        "ETH-USD",
        res,
        start,
        end,
    )

    # then
    amount = cu.amount_of_candles_in_range(start, end, res)
    assert len(candles) == amount
    assert candles[-1].started_at == start
    assert candles[0].started_at == end - timedelta(seconds=res.seconds)


@pytest.mark.parametrize("amount", amounts)
@pytest.mark.parametrize("resolution", resolutions_reduced)
@pytest.mark.asyncio
async def test_v3_fetch_cluster_is_up_to_date(
    dydx_v3_candle_fetcher_mainnet: DydxV3CandleFetcher,
    amount: int,
    resolution: ResolutionDetail,
) -> None:
    # given
    fetcher = dydx_v3_candle_fetcher_mainnet
    res = resolution
    amount_back = amount
    now_rounded = cu.norm_date(now_utc_iso(), res)
    start_date = now_rounded - timedelta(seconds=res.seconds * amount_back)

    candles = await fetcher.fetch_candles_up_to_now(
        "ETH-USD",
        res,
        start_date,
    )

    # then
    cu.assert_candle_unity(candles)
    cu.assert_chronologic_order(candles)
    assert cu.is_newest_valid_candle(candles[0])
    assert len(candles) >= amount_back


# TODO: See if on V3 missing as well... if not remove test
# NOTE: This test exists only to see, wether the backend is being maintained to sometime include this candle again or not (which I'm sure will not happen).
# Order violated from Candles None (2024-07-25 06:52:00+00:00) to None (2024-07-25 06:54:00+00:00)
# Meaning: The (mainnet!) backend is actually missing one candle (which startedAt 2024-07-25 06:53:00+00:00)
@pytest.mark.skip(reason="This is only to check if dYdX fixed their missing candle.")
@pytest.mark.asyncio
async def test_candle_error_at_2024_07_25_06_52(
    dydx_v3_candle_fetcher_mainnet: DydxV3CandleFetcher,
) -> None:
    # given
    res = DydxResolution.ONE_MINUTE
    fetcher = dydx_v3_candle_fetcher_mainnet
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
