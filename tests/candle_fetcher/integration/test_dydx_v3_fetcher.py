from datetime import timedelta
import pytest

from dydx3 import Client  # type: ignore
from dydx3.constants import API_HOST_SEPOLIA  # type: ignore

from dydx_v4_client.indexer.rest.indexer_client import IndexerClient  # type: ignore
from dydx_v4_client.network import TESTNET  # type: ignore

from sir_utilities.date_time import string_to_datetime


from locast.candle.candle_utility import CandleUtility as cu
from locast.candle.resolution import ResolutionDetail, Seconds
from locast.candle_fetcher.dydx.api_fetcher.dydx_v3_fetcher import DydxV3Fetcher
from locast.candle_fetcher.dydx.api_fetcher.dydx_v4_fetcher import DydxV4Fetcher


# NOTE: TDD in order to find a fix for dydx v3 "backend magic"
@pytest.mark.asyncio
async def test_v3_fetch_range_of_one_candle_returns_one_candle() -> None:
    # given
    testnet_client = Client(host=API_HOST_SEPOLIA)
    api_fetcher = DydxV3Fetcher(testnet_client)

    market = "ETH-USD"
    res = ResolutionDetail(Seconds.ONE_MINUTE, "1MIN")
    start = string_to_datetime("2024-04-01T00:00:00.000Z")
    end = string_to_datetime("2024-04-01T00:01:00.000Z")

    # when
    candles = await api_fetcher.fetch(
        market,
        res,
        start,
        end,
    )

    # then
    amount = cu.amount_of_candles_in_range(start, end, res)
    assert len(candles) == amount
    assert candles[-1].started_at == start
    assert candles[0].started_at == end - timedelta(seconds=res.seconds)


# Identical test on v4 backend...
@pytest.mark.asyncio
async def test_v4_fetch_range_of_one_candle_returns_one_candle() -> None:
    # given
    testnet_client = IndexerClient(TESTNET.rest_indexer)
    api_fetcher = DydxV4Fetcher(testnet_client)

    market = "ETH-USD"
    res = ResolutionDetail(Seconds.ONE_MINUTE, "1MIN")
    start = string_to_datetime("2024-04-01T00:00:00.000Z")
    end = string_to_datetime("2024-04-01T00:01:00.000Z")

    # when
    candles = await api_fetcher.fetch(
        market,
        res,
        start,
        end,
    )

    # then
    amount = cu.amount_of_candles_in_range(start, end, res)
    assert len(candles) == amount
    assert candles[-1].started_at == start
    assert candles[0].started_at == end - timedelta(seconds=res.seconds)
