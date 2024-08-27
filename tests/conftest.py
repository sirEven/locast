from typing import AsyncGenerator, Generator
import pytest
import pytest_asyncio

from dydx_v4_client.indexer.rest.indexer_client import IndexerClient  # type: ignore
from dydx_v4_client.network import TESTNET, make_mainnet  # type: ignore

from sqlmodel import Session
from sqlmodel.pool import StaticPool
from sqlalchemy import Engine, create_engine

from sir_utilities.date_time import string_to_datetime

from locast.candle.candle import Candle
from locast.candle.dydx.dydx_candle_mapping import DydxV4CandleMapping
from locast.candle.dydx.dydx_resolution import DydxResolution
from locast.candle.exchange_candle_mapper import ExchangeCandleMapper
from locast.candle_fetcher.dydx.api_fetcher.dydx_v4_fetcher import DydxV4Fetcher
from locast.candle_fetcher.dydx.candle_fetcher.dydx_v4_candle_fetcher import (
    DydxV4CandleFetcher,
)
from locast.candle_storage.sql.sqlite_candle_storage import SqliteCandleStorage
from locast.live_candle.dydx.dydx_live_candle import DydxV4LiveCandle

from locast.candle.candle_utility import CandleUtility as cu

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
def dydx_v4_eth_one_min_mock_candles() -> Generator[list[Candle], None, None]:
    start_str = "2024-01-01T00:00:00+00:00"
    end_str = "2024-01-02T00:00:00+00:00"
    market = "ETH-USD"
    resolution = DydxResolution.ONE_MINUTE
    start = string_to_datetime(start_str)
    end = string_to_datetime(end_str)
    amount = cu.amount_of_candles_in_range(start, end, resolution.seconds)
    eth_dicts = mock_dydx_v4_candle_dict_batch(
        resolution.notation,
        market,
        start_str,
        end_str,
        batch_size=amount,
    )
    mapper = ExchangeCandleMapper(DydxV4CandleMapping())
    yield mapper.to_candles(eth_dicts)


@pytest_asyncio.fixture  # type: ignore
async def dydx_v4_live_candle() -> AsyncGenerator[DydxV4LiveCandle, None]:
    eth_usd = "ETH-USD"
    btc_usd = "BTC-USD"
    one_min = DydxResolution.ONE_MINUTE.notation
    markets_per_resolution = {one_min: [eth_usd, btc_usd]}
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


@pytest.fixture
def sqlite_engine() -> Generator[Engine, None, None]:
    yield create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


@pytest.fixture
def sqlite_session(sqlite_engine: Engine) -> Generator[Session, None, None]:
    with Session(sqlite_engine) as session:
        yield session


@pytest.fixture
def sqlite_candle_storage_memory(
    sqlite_engine: Engine,
) -> Generator[SqliteCandleStorage, None, None]:
    yield SqliteCandleStorage(sqlite_engine)
