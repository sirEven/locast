from typing import AsyncGenerator, Generator, List
import pytest
import pytest_asyncio

from dydx_v4_client.indexer.rest.indexer_client import IndexerClient  # type: ignore
from dydx_v4_client.network import TESTNET, make_mainnet  # type: ignore
from dydx3 import Client  # type: ignore
from dydx3.constants import API_HOST_SEPOLIA, API_HOST_MAINNET  # type: ignore


from sqlmodel import Session
from sqlmodel.pool import StaticPool
from sqlalchemy import Engine, create_engine

from sir_utilities.date_time import string_to_datetime

from locast.candle.candle import Candle
from locast.candle.dydx.dydx_candle_mapping import DydxV4CandleMapping
from locast.candle.dydx.dydx_resolution import DydxResolution
from locast.candle.exchange import Exchange
from locast.candle.exchange_candle_mapper import ExchangeCandleMapper
from locast.candle_fetcher.dydx.api_fetcher.dydx_v3_fetcher import DydxV3Fetcher
from locast.candle_fetcher.dydx.api_fetcher.dydx_v4_fetcher import DydxV4Fetcher
from locast.candle_fetcher.dydx.candle_fetcher.dydx_candle_fetcher import (
    DydxCandleFetcher,
)
from locast.candle_storage.sql.sqlite_candle_storage import SqliteCandleStorage

from locast.candle.candle_utility import CandleUtility as cu

from locast.store_manager.store_manager import StoreManager
from tests.helper.candle_mockery.v3_client_mock import V3ClientMock
from tests.helper.candle_mockery.v4_indexer_mock import V4IndexerClientMock
from tests.helper.candle_mockery.mock_dydx_candle_dicts import (
    mock_dydx_candle_dict_batch,
)


import nest_asyncio  # type: ignore

# region - Testing Setup
# Prevent asyncio "runloop already running" error
nest_asyncio.apply()  # type: ignore


# NOTE: Mark all tests inside an integration directory as integration tests, which we exclude in CI.
def pytest_collection_modifyitems(config: pytest.Config, items: List[pytest.Item]):
    for item in items:
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)


# endregion

MAINNET = make_mainnet(
    rest_indexer="https://indexer.dydx.trade/",
    websocket_indexer="wss://indexer.dydx.trade/v4/ws",
    node_url="dydx-ops-rpc.kingnodes.com:443",
)


# region - Candles
@pytest.fixture
def dydx_v4_eth_one_min_mock_candles() -> Generator[list[Candle], None, None]:
    start_str = "2024-01-01T00:00:00+00:00"
    end_str = "2024-01-02T00:00:00+00:00"
    market = "ETH-USD"
    resolution = DydxResolution.ONE_MINUTE
    start = string_to_datetime(start_str)
    end = string_to_datetime(end_str)
    amount = cu.amount_of_candles_in_range(start, end, resolution)
    eth_dicts = mock_dydx_candle_dict_batch(
        Exchange.DYDX_V4,
        resolution.notation,
        market,
        start_str,
        end_str,
        batch_size=amount,
    )
    mapper = ExchangeCandleMapper(DydxV4CandleMapping())
    yield mapper.to_candles(eth_dicts)


# region - dYdX v4
@pytest_asyncio.fixture  # type: ignore
async def dydx_v4_fetcher_mock() -> AsyncGenerator[DydxV4Fetcher, None]:
    mock_client = V4IndexerClientMock()
    yield DydxV4Fetcher(mock_client)


@pytest_asyncio.fixture  # type: ignore
async def dydx_v4_candle_fetcher_mock(
    dydx_v4_fetcher_mock: DydxV4Fetcher,
) -> AsyncGenerator[DydxCandleFetcher, None]:
    yield DydxCandleFetcher(api_fetcher=dydx_v4_fetcher_mock)


@pytest_asyncio.fixture  # type: ignore
async def dydx_v4_candle_fetcher_testnet() -> AsyncGenerator[DydxCandleFetcher, None]:
    testnet_client = IndexerClient(TESTNET.rest_indexer)
    yield DydxCandleFetcher(api_fetcher=DydxV4Fetcher(testnet_client))


@pytest_asyncio.fixture  # type: ignore
async def dydx_v4_candle_fetcher_mainnet() -> AsyncGenerator[DydxCandleFetcher, None]:
    mainnet_client = IndexerClient(MAINNET.rest_indexer)
    yield DydxCandleFetcher(api_fetcher=DydxV4Fetcher(mainnet_client))


# region - dYdX v3
@pytest_asyncio.fixture  # type: ignore
async def dydx_v3_fetcher_mock() -> AsyncGenerator[DydxV3Fetcher, None]:
    mock_client = V3ClientMock()
    yield DydxV3Fetcher(mock_client)


@pytest_asyncio.fixture  # type: ignore
async def dydx_v3_candle_fetcher_mock(
    dydx_v3_fetcher_mock: DydxV3Fetcher,
) -> AsyncGenerator[DydxCandleFetcher, None]:
    yield DydxCandleFetcher(api_fetcher=dydx_v3_fetcher_mock)


@pytest_asyncio.fixture  # type: ignore
async def dydx_v3_candle_fetcher_testnet() -> AsyncGenerator[DydxCandleFetcher, None]:
    testnet_client = Client(host=API_HOST_SEPOLIA)
    yield DydxCandleFetcher(api_fetcher=DydxV3Fetcher(testnet_client))


@pytest_asyncio.fixture  # type: ignore
async def dydx_v3_candle_fetcher_mainnet() -> AsyncGenerator[DydxCandleFetcher, None]:
    mainnet_client = Client(host=API_HOST_MAINNET)
    yield DydxCandleFetcher(api_fetcher=DydxV3Fetcher(mainnet_client))


# region - mock fetchers

# endregion


# region - SQLite
@pytest.fixture
def sqlite_engine_in_memory() -> Generator[Engine, None, None]:
    yield create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


@pytest.fixture
def sqlite_session_in_memory(
    sqlite_engine_in_memory: Engine,
) -> Generator[Session, None, None]:
    with Session(sqlite_engine_in_memory) as session:
        yield session


@pytest.fixture
def sqlite_candle_storage_memory(
    sqlite_engine_in_memory: Engine,
) -> Generator[SqliteCandleStorage, None, None]:
    yield SqliteCandleStorage(sqlite_engine_in_memory)


# endregion


# region - StoreManager
@pytest.fixture
def store_manager_mock_memory(
    dydx_v4_candle_fetcher_mock: DydxCandleFetcher,
    sqlite_candle_storage_memory: SqliteCandleStorage,
) -> Generator[StoreManager, None, None]:
    yield StoreManager(
        candle_fetcher=dydx_v4_candle_fetcher_mock,
        candle_storage=sqlite_candle_storage_memory,
    )


# endregion
