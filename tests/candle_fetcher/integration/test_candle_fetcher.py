from datetime import timedelta

import pytest

from sir_utilities.date_time import now_utc_iso, string_to_datetime

from locast.candle.candle_utility import CandleUtility as cu
from locast.candle.exchange_resolution import ResolutionDetail

from locast.candle_fetcher.candle_fetcher import CandleFetcher
from tests.helper.parametrization.list_of_amounts import amounts
from tests.helper.parametrization.list_of_resolution_details import resolutions

from tests.helper.fixture_helpers import get_typed_fixture


# COLLABORATION: Add additional fixture names into these lists, that deliver candle fetcher implementations that conform to CandleFetcher:
# - testnet list (if the exchange provides a testnet)
# - mainnet list
# They will be included in the integration tests for candle fetcher components.

testnet_candle_fetchers = [
    "dydx_v4_candle_fetcher_testnet",
]

mainnet_candle_fetchers = [
    "dydx_v4_candle_fetcher_mainnet",
]

resolutions_reduced = resolutions[:-2]  # Backend too young still


@pytest.mark.parametrize("resolution", resolutions_reduced)
@pytest.mark.parametrize("candle_fetcher_testnet", testnet_candle_fetchers)
@pytest.mark.asyncio
async def test_fetch_range_of_candles_testnet(
    request: pytest.FixtureRequest,
    candle_fetcher_testnet: str,
    resolution: ResolutionDetail,
) -> None:
    # given
    fetcher = get_typed_fixture(request, candle_fetcher_testnet, CandleFetcher)
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
    assert candles[-1].started_at == start
    assert candles[0].started_at == end - timedelta(seconds=res.seconds)


@pytest.mark.parametrize("resolution", resolutions_reduced)
@pytest.mark.parametrize("candle_fetcher_mainnet", mainnet_candle_fetchers)
@pytest.mark.asyncio
async def test_fetch_range_of_candles_mainnet(
    request: pytest.FixtureRequest,
    candle_fetcher_mainnet: str,
    resolution: ResolutionDetail,
) -> None:
    # given
    fetcher = get_typed_fixture(request, candle_fetcher_mainnet, CandleFetcher)
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
    assert candles[-1].started_at == start
    assert candles[0].started_at == end - timedelta(seconds=res.seconds)


@pytest.mark.parametrize("amount", amounts)
@pytest.mark.parametrize("resolution", resolutions_reduced)
@pytest.mark.parametrize("candle_fetcher_mainnet", mainnet_candle_fetchers)
@pytest.mark.asyncio
async def test_fetch_cluster_is_up_to_date(
    request: pytest.FixtureRequest,
    candle_fetcher_mainnet: str,
    amount: int,
    resolution: ResolutionDetail,
) -> None:
    # given
    fetcher = get_typed_fixture(request, candle_fetcher_mainnet, CandleFetcher)
    res = resolution
    amount_back = amount
    now_rounded = cu.norm_date(now_utc_iso(), res)
    start_date = now_rounded - timedelta(seconds=res.seconds * amount_back)

    # when
    candles = await fetcher.fetch_candles_up_to_now(
        "ETH-USD",
        res,
        start_date,
    )

    # then
    cu.assert_candle_unity(candles)
    assert cu.is_newest_valid_candle(candles[0])
