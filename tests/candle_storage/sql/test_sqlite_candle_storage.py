# WIP: Continue testing
# NOTE: Write async tests like in test_dydx_v4_candle_fetcher.py
from typing import List, Type
import pytest
from sqlalchemy import Engine, MetaData
from sqlmodel import SQLModel, Session, select

from sir_utilities.date_time import string_to_datetime

from locast.candle.resolution import ResolutionDetail, Seconds
from locast.candle_storage.sql.sqlite_candle_storage import SqliteCandleStorage
from locast.candle_storage.sql.tables import (
    SqliteCandle,
    SqliteExchange,
    SqliteMarket,
    SqliteResolution,
)

from tests.helper.candle_mockery.mock_dydx_v4_candles import mock_dydx_v4_candles
from tests.helper.parametrization.list_of_amounts import amounts

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


# store this batch in storage and verify that tables have right amount of rows and correct values (all tables)
@pytest.mark.parametrize("amount", amounts)
def test_store_candles_results_in_correct_storage_state(
    sqlite_candle_storage_memory: SqliteCandleStorage,
    amount: int,
) -> None:
    # given
    storage = sqlite_candle_storage_memory
    res = ResolutionDetail(Seconds.ONE_MINUTE, "1MIN")
    start_date = string_to_datetime("2022-01-01T00:00:00.000Z")
    market = "ETH-USD"

    candles = mock_dydx_v4_candles(market, res, amount, start_date)
    print(candles)

    # when
    # WIP: Continue!


def _table_exists(engine: Engine, table: Type[SQLModel]) -> bool:
    metadata = MetaData()
    metadata.reflect(bind=engine)
    return table.__tablename__ in metadata.tables  # type: ignore


def _table_is_empty(sqlite_session_in_memory: Session, table: Type[SQLModel]) -> bool:
    statement = select(table)
    result = sqlite_session_in_memory.exec(statement)
    return result.first() is None
