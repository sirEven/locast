from typing import AsyncGenerator
import pytest_asyncio

from locast.candle.dydx.dydx_resolution import DydxResolution
from locast.candle_fetcher.dydx.fetcher.dydx_v4_fetcher import DydxV4Fetcher
from locast.candle_fetcher.dydx.dydx_candle_fetcher import DydxCandleFetcher
from locast.live_candle.dydx.dydx_live_candle import DydxV4LiveCandle

from dydx_v4_client.indexer.rest.indexer_client import IndexerClient  # type: ignore
from dydx_v4_client.network import TESTNET, make_mainnet  # type: ignore

from tests.helper.candle_mockery.v4_indexer_mock import V4IndexerClientMock

ETH_USD = "ETH-USD"
BTC_USD = "BTC-USD"
LINK_USD = "LINK-USD"
ONE_MIN = DydxResolution.ONE_MINUTE

MAINNET = make_mainnet(
    rest_indexer="https://indexer.dydx.trade/",
    websocket_indexer="wss://indexer.dydx.trade/v4/ws",
    node_url="dydx-ops-rpc.kingnodes.com:443",
)


@pytest_asyncio.fixture  # type: ignore
async def dydx_v4_live_candle() -> AsyncGenerator[DydxV4LiveCandle, None]:
    markets_per_resolution = {ONE_MIN.notation: [ETH_USD, BTC_USD]}
    live_candle = DydxV4LiveCandle(
        host_url=TESTNET.websocket_indexer,
        markets_per_resolution=markets_per_resolution,
    )

    yield live_candle
    await live_candle.stop()


@pytest_asyncio.fixture  # type: ignore
async def mock_dydx_v4_candle_fetcher() -> AsyncGenerator[DydxCandleFetcher, None]:
    mock_client = V4IndexerClientMock()
    yield DydxCandleFetcher(api_fetchers=[DydxV4Fetcher(mock_client)])


@pytest_asyncio.fixture  # type: ignore
async def dydx_v4_candle_fetcher_testnet() -> AsyncGenerator[DydxCandleFetcher, None]:
    testnet_client = IndexerClient(TESTNET.rest_indexer)
    yield DydxCandleFetcher(api_fetchers=[DydxV4Fetcher(testnet_client)])


@pytest_asyncio.fixture  # type: ignore
async def dydx_v4_candle_fetcher_mainnet() -> AsyncGenerator[DydxCandleFetcher, None]:
    mainnet_client=IndexerClient(MAINNET.rest_indexer)
    yield DydxCandleFetcher(api_fetchers=[DydxV4Fetcher(mainnet_client)])
    
