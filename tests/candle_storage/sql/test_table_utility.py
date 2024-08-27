from sqlmodel import Session
from locast.candle.dydx.dydx_resolution import DydxResolution
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
    # given a database with non-empty exchange table
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


def test_look_up_sql_market_returns_none(
    sqlite_session: Session,
    sqlite_candle_storage_memory: SqliteCandleStorage,
) -> None:
    # given a database with empty market table
    _ = sqlite_candle_storage_memory
    table_utility = TableUtility()
    market = "ETH-USD"

    # when
    sql_market = table_utility.lookup_sql_market(market, sqlite_session)

    # then
    assert sql_market is None


def test_look_up_sql_market_returns_correctly(
    sqlite_session: Session,
    sqlite_candle_storage_memory: SqliteCandleStorage,
) -> None:
    # given a database with non-empty market table
    _ = sqlite_candle_storage_memory
    table_utility = TableUtility()
    market = "ETH-USD"
    table_utility.lookup_or_create_sql_market(market, sqlite_session)

    # when
    sql_market = table_utility.lookup_sql_market(market, sqlite_session)

    # then
    assert sql_market is not None
    assert sql_market.market == market
    assert sql_market.id is not None


def test_look_up_sql_resolution_returns_none(
    sqlite_session: Session,
    sqlite_candle_storage_memory: SqliteCandleStorage,
) -> None:
    # given a database with empty resolution table
    _ = sqlite_candle_storage_memory
    table_utility = TableUtility()
    resolution = DydxResolution.ONE_MINUTE.seconds

    # when
    sql_resolution = table_utility.lookup_sql_resolution(resolution, sqlite_session)

    # then
    assert sql_resolution is None


def test_look_up_sql_resolution_returns_correctly(
    sqlite_session: Session,
    sqlite_candle_storage_memory: SqliteCandleStorage,
) -> None:
    # given a database with non-empty resolution table
    _ = sqlite_candle_storage_memory
    table_utility = TableUtility()
    resolution = DydxResolution.ONE_MINUTE.seconds
    table_utility.lookup_or_create_sql_resolution(resolution, sqlite_session)

    # when
    sql_resolution = table_utility.lookup_sql_resolution(resolution, sqlite_session)

    # then
    assert sql_resolution is not None
    assert sql_resolution.resolution == resolution
    assert sql_resolution.id is not None