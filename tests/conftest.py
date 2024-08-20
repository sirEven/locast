from decimal import Decimal
from typing import AsyncGenerator, Generator
import pytest
import pytest_asyncio

from sir_utilities.date_time import now_utc_iso, string_to_datetime

from locast.candle.candle import Candle
from locast.candle.dydx.dydx_resolution import DydxResolution
from locast.candle.exchange import Exchange
from locast.candle.exchange_candle_mapper import ExchangeCandleMapper
from locast.candle.resolution import ResolutionDetail
from locast.candle_fetcher.dydx.api_fetcher.dydx_v4_fetcher import DydxV4Fetcher
from locast.candle_fetcher.dydx.candle_fetcher.dydx_v4_candle_fetcher import (
    DydxV4CandleFetcher,
)
from locast.live_candle.dydx.dydx_live_candle import DydxV4LiveCandle

from locast.candle.candle_utility import CandleUtility as cu

from dydx_v4_client.indexer.rest.indexer_client import IndexerClient  # type: ignore
from dydx_v4_client.network import TESTNET, make_mainnet  # type: ignore

from tests.helper.candle_mockery.v4_indexer_mock import V4IndexerClientMock
from tests.helper.candle_mockery.mock_dydx_v4_candle_dicts import (
    mock_dydx_v4_candle_dict_batch,
)


MAINNET = make_mainnet(
    rest_indexer="https://indexer.dydx.trade/",
    websocket_indexer="wss://indexer.dydx.trade/v4/ws",
    node_url="dydx-ops-rpc.kingnodes.com:443",
)


@pytest.fixture
def eth_usd() -> str:
    return "ETH-USD"


@pytest.fixture
def btc_usd() -> str:
    return "BTC-USD"


@pytest.fixture
def link_usd() -> str:
    return "LINK-USD"


@pytest.fixture
def one_min() -> ResolutionDetail:
    return DydxResolution.ONE_MINUTE


@pytest.fixture
def dummy_candle() -> Generator[Candle, None, None]:
    yield Candle(
        None,
        Exchange.DYDX_V4,
        "ETH-USD",
        DydxResolution.ONE_MINUTE.seconds,
        now_utc_iso(),
        Decimal("100"),
        Decimal("100"),
        Decimal("100"),
        Decimal("100"),
        Decimal("100"),
        10,
        Decimal("100"),
        Decimal("100"),
    )


@pytest.fixture
def dydx_v4_eth_one_min_mock_candles() -> Generator[list[Candle], None, None]:
    start_str = "2024-01-01T00:00:00+00:00"
    end_str = "2024-01-05T00:00:00+00:00"
    exchange = Exchange.DYDX_V4
    market = "ETH-USD"
    resolution = DydxResolution.ONE_MINUTE.seconds

    start_str = "2024-01-01T00:00:00+00:00"
    end_str = "2024-01-05T00:00:00+00:00"
    start = string_to_datetime(start_str)
    end = string_to_datetime(end_str)
    amount = cu.amount_of_candles_in_range(start, end, resolution)
    eth_dicts = mock_dydx_v4_candle_dict_batch(
        DydxResolution.ONE_MINUTE.notation,
        market,
        start_str,
        end_str,
        batch_size=amount,
    )

    yield ExchangeCandleMapper.to_candles(exchange, eth_dicts)


@pytest_asyncio.fixture  # type: ignore
async def dydx_v4_live_candle(
    eth_usd: str,
    btc_usd: str,
    one_min: ResolutionDetail,
) -> AsyncGenerator[DydxV4LiveCandle, None]:
    markets_per_resolution = {one_min.notation: [eth_usd, btc_usd]}
    live_candle = DydxV4LiveCandle(
        host_url=TESTNET.websocket_indexer,
        markets_per_resolution=markets_per_resolution,
    )

    yield live_candle
    await live_candle.stop()


@pytest_asyncio.fixture  # type: ignore
async def mock_dydx_v4_candle_fetcher() -> AsyncGenerator[DydxV4CandleFetcher, None]:
    mock_client = V4IndexerClientMock()
    yield DydxV4CandleFetcher(api_fetcher=DydxV4Fetcher(mock_client))


@pytest_asyncio.fixture  # type: ignore
async def dydx_v4_candle_fetcher_testnet() -> AsyncGenerator[DydxV4CandleFetcher, None]:
    testnet_client = IndexerClient(TESTNET.rest_indexer)
    yield DydxV4CandleFetcher(api_fetcher=DydxV4Fetcher(testnet_client))


@pytest_asyncio.fixture  # type: ignore
async def dydx_v4_candle_fetcher_mainnet() -> AsyncGenerator[DydxV4CandleFetcher, None]:
    mainnet_client = IndexerClient(MAINNET.rest_indexer)
    yield DydxV4CandleFetcher(api_fetcher=DydxV4Fetcher(mainnet_client))
