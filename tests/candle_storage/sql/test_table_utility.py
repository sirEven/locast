from sqlmodel import Session
from locast.candle.exchange import Exchange
from locast.candle_storage.sql.sqlite_candle_storage import SqliteCandleStorage
from locast.candle_storage.sql.table_utility import TableUtility


def test_look_up_sql_exchange_returns_none(
    sqlite_session: Session,
    sqlite_candle_storage_memory: SqliteCandleStorage,
) -> None:
    # given a database with empty exchange table
    _ = sqlite_candle_storage_memory
    table_utility = TableUtility()
    exchange = Exchange.DYDX_V4

    # when
    sql_exchange = table_utility.lookup_sql_exchange(exchange, sqlite_session)

    # then
    assert sql_exchange is None


def test_look_up_sql_exchange_returns_correctly(
    sqlite_session: Session,
    sqlite_candle_storage_memory: SqliteCandleStorage,
) -> None:
    # given a database with exchange table that holds exchange
    _ = sqlite_candle_storage_memory
    table_utility = TableUtility()
    exchange = Exchange.DYDX_V4
    table_utility.lookup_or_create_sql_exchange(exchange, sqlite_session)

    # when
    sql_exchange = table_utility.lookup_sql_exchange(exchange, sqlite_session)

    # then
    assert sql_exchange is not None
    assert sql_exchange.exchange == exchange
    assert sql_exchange.id is not None
