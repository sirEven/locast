from datetime import timedelta
from typing import List, Type
import pytest
from sqlalchemy import Engine, MetaData
from sqlmodel import SQLModel, Session, select

from sir_utilities.date_time import string_to_datetime

from locast.candle.exchange import Exchange
from locast.candle.resolution import ResolutionDetail, Seconds
from locast.candle_storage.sql.table_utility import TableUtility as tu
from locast.candle_storage.sql.sqlite_candle_storage import SqliteCandleStorage
from locast.candle_storage.sql.tables import (
    SqliteCandle,
    SqliteExchange,
    SqliteMarket,
    SqliteResolution,
)

from locast.candle.candle_utility import CandleUtility as cu


from tests.helper.candle_mockery.mock_dydx_v4_candles import (
    mock_dydx_v4_candle_range,
    mock_dydx_v4_candles,
)

from tests.helper.parametrization.list_of_amounts import few_amounts

tables: List[Type[SQLModel]] = [
    SqliteExchange,
    SqliteMarket,
    SqliteResolution,
    SqliteCandle,
]


@pytest.mark.parametrize("table", tables)
def test_initialization_creates_all_tables_empty(
    sqlite_engine_in_memory: Engine,
    table: Type[SQLModel],
) -> None:
    # given
    _ = SqliteCandleStorage(sqlite_engine_in_memory)

    # when & then
    assert _table_exists(sqlite_engine_in_memory, table)
    assert _table_is_empty(Session(sqlite_engine_in_memory), table)


@pytest.mark.parametrize("amount", few_amounts)
@pytest.mark.asyncio
async def test_store_candles_results_in_correct_storage_state(
    sqlite_engine_in_memory: Engine,
    sqlite_candle_storage_memory: SqliteCandleStorage,
    amount: int,
) -> None:
    # given
    engine = sqlite_engine_in_memory
    storage = sqlite_candle_storage_memory

    res = ResolutionDetail(Seconds.ONE_MINUTE, "1MIN")
    start_date = string_to_datetime("2022-01-01T00:00:00.000Z")
    market = "ETH-USD"

    candles = mock_dydx_v4_candles(market, res, amount, start_date)

    # when
    await storage.store_candles(candles)

    # then
    assert _table_has_amount_of_rows(engine, SqliteCandle, amount)
    assert _table_has_amount_of_rows(engine, SqliteExchange, 1)
    assert _table_has_amount_of_rows(engine, SqliteMarket, 1)
    assert _table_has_amount_of_rows(engine, SqliteResolution, 1)


@pytest.mark.parametrize("amount", few_amounts)
@pytest.mark.asyncio
async def test_retrieve_candles_results_in_correct_cluster(
    sqlite_candle_storage_memory: SqliteCandleStorage,
    amount: int,
) -> None:
    # given
    storage = sqlite_candle_storage_memory

    exchange = Exchange.DYDX_V4
    res = ResolutionDetail(Seconds.ONE_MINUTE, "1MIN")
    start_date = string_to_datetime("2022-01-01T00:00:00.000Z")
    market = "ETH-USD"

    candles = mock_dydx_v4_candles(market, res, amount, start_date)
    await storage.store_candles(candles)

    # when
    retrieved_candles = await storage.retrieve_cluster(exchange, market, res.seconds)

    # then
    assert len(retrieved_candles) == amount
    assert retrieved_candles[0].exchange == exchange
    assert retrieved_candles[0].market == market
    assert retrieved_candles[0].resolution == res.seconds


@pytest.mark.asyncio
async def test_retrieve_candles_results_in_empty_list(
    sqlite_candle_storage_memory: SqliteCandleStorage,
) -> None:
    # given
    storage = sqlite_candle_storage_memory

    exchange = Exchange.DYDX_V4
    res = ResolutionDetail(Seconds.ONE_MINUTE, "1MIN")
    market = "ETH-USD"

    # when no cluster in storage
    retrieved_candles = await storage.retrieve_cluster(exchange, market, res.seconds)

    # then
    assert len(retrieved_candles) == 0


@pytest.mark.parametrize("amount", few_amounts)
@pytest.mark.asyncio
async def test_delete_cluster_results_in_correct_state(
    sqlite_engine_in_memory: Engine,
    sqlite_candle_storage_memory: SqliteCandleStorage,
    amount: int,
) -> None:
    # given
    engine = sqlite_engine_in_memory
    storage = sqlite_candle_storage_memory

    exchange = Exchange.DYDX_V4
    res = ResolutionDetail(Seconds.ONE_MINUTE, "1MIN")
    start_date = string_to_datetime("2022-01-01T00:00:00.000Z")
    market = "ETH-USD"

    candles = mock_dydx_v4_candles(market, res, amount, start_date)
    await storage.store_candles(candles)

    # when
    await storage.delete_cluster(exchange, market, res.seconds)

    # then
    assert _table_has_amount_of_rows(engine, SqliteCandle, 0)
    assert _table_has_amount_of_rows(engine, SqliteExchange, 1)
    assert _table_has_amount_of_rows(engine, SqliteMarket, 1)
    assert _table_has_amount_of_rows(engine, SqliteResolution, 1)


@pytest.mark.asyncio
async def test_get_cluster_head_results_in_newest_candle(
    sqlite_candle_storage_memory: SqliteCandleStorage,
) -> None:
    # given
    storage = sqlite_candle_storage_memory

    exchange = Exchange.DYDX_V4
    market = "ETH-USD"
    res = ResolutionDetail(Seconds.ONE_MINUTE, "1MIN")

    start_date = string_to_datetime("2024-01-01T00:00:00.000Z")
    end_date = string_to_datetime("2024-01-01T00:05:00.000Z")

    candles = mock_dydx_v4_candle_range(market, res, start_date, end_date)
    await storage.store_candles(candles)

    # when
    cluster_info = await storage.get_cluster_info(exchange, market, res.seconds)

    # then
    expected_started_at = end_date - timedelta(seconds=res.seconds)
    assert cluster_info.head
    assert cluster_info.head.started_at == expected_started_at


@pytest.mark.asyncio
async def test_get_cluster_head_results_in_None(
    sqlite_candle_storage_memory: SqliteCandleStorage,
) -> None:
    # given
    storage = sqlite_candle_storage_memory

    exchange = Exchange.DYDX_V4
    market = "ETH-USD"
    res = ResolutionDetail(Seconds.ONE_MINUTE, "1MIN")

    # when
    cluster_info = await storage.get_cluster_info(exchange, market, res.seconds)

    # then
    assert cluster_info.head is None
    assert cluster_info.tail is None
    assert cluster_info.amount == 0
    assert cluster_info.is_uptodate is False


@pytest.mark.asyncio
async def test_get_cluster_head_when_foreign_tables_exist_results_in_None(
    sqlite_session_in_memory: Session,
    sqlite_candle_storage_memory: SqliteCandleStorage,
) -> None:
    # given
    storage = sqlite_candle_storage_memory

    exchange = Exchange.DYDX_V4
    market = "ETH-USD"
    res = ResolutionDetail(Seconds.ONE_MINUTE, "1MIN")

    tu.lookup_or_insert_sqlite_exchange(exchange, sqlite_session_in_memory)
    tu.lookup_or_insert_sqlite_market(market, sqlite_session_in_memory)
    tu.lookup_or_insert_sqlite_resolution(res.seconds, sqlite_session_in_memory)

    # when
    cluster_info = await storage.get_cluster_info(exchange, market, res.seconds)

    # then
    assert cluster_info.head is None
    assert cluster_info.tail is None
    assert cluster_info.amount == 0
    assert cluster_info.is_uptodate is False


@pytest.mark.asyncio
async def test_get_cluster_info_results_in_correct_info(
    sqlite_candle_storage_memory: SqliteCandleStorage,
) -> None:
    # given
    storage = sqlite_candle_storage_memory

    exchange = Exchange.DYDX_V4
    market = "ETH-USD"
    res = ResolutionDetail(Seconds.ONE_MINUTE, "1MIN")

    start_date = string_to_datetime("2024-01-01T00:00:00.000Z")
    end_date = string_to_datetime("2024-01-01T00:05:00.000Z")

    candles = mock_dydx_v4_candle_range(market, res, start_date, end_date)
    candles[0].started_at = cu.normalized_now(res.seconds) - timedelta(
        seconds=res.seconds
    )
    await storage.store_candles(candles)

    # when
    cluster_info = await storage.get_cluster_info(exchange, market, res.seconds)

    # then
    expected_head = candles[0]
    expected_tail = candles[-1]
    assert cluster_info.head and cluster_info.tail
    assert cluster_info.head.started_at == expected_head.started_at
    assert cluster_info.tail.started_at == expected_tail.started_at
    assert cluster_info.amount == len(candles)
    assert cluster_info.is_uptodate


@pytest.mark.asyncio
async def test_get_cluster_info_results_in_none(
    sqlite_session_in_memory: Session,
    sqlite_candle_storage_memory: SqliteCandleStorage,
) -> None:
    # given
    storage = sqlite_candle_storage_memory

    exchange = Exchange.DYDX_V4
    market = "ETH-USD"
    res = ResolutionDetail(Seconds.ONE_MINUTE, "1MIN")

    # when
    cluster_info = await storage.get_cluster_info(exchange, market, res.seconds)

    # then
    assert cluster_info.head is None
    assert cluster_info.tail is None
    assert cluster_info.amount == 0
    assert cluster_info.is_uptodate is False


def _table_exists(engine: Engine, table: Type[SQLModel]) -> bool:
    metadata = MetaData()
    metadata.reflect(bind=engine)
    return table.__tablename__ in metadata.tables  # type: ignore


def _table_is_empty(sqlite_session_in_memory: Session, table: Type[SQLModel]) -> bool:
    statement = select(table)
    result = sqlite_session_in_memory.exec(statement)
    return result.first() is None


def _table_has_amount_of_rows(
    sqlite_engine: Engine,
    table: Type[SQLModel],
    amount: int,
) -> bool:
    with Session(sqlite_engine) as session:
        statement = select(table)
        result = session.exec(statement).all()
        return amount == len(result)
