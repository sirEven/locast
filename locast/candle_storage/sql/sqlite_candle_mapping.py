from decimal import Decimal

from sqlalchemy import Engine
from sqlmodel import Session


from locast.candle.candle import Candle
from locast.candle_storage.database_candle_mapping import DatabaseCandleMapping
from locast.candle_storage.sql.tables import (
    SqliteCandle,
)
from locast.candle_storage.sql.table_utility import TableAccess as ta


class SqliteCandleMapping(DatabaseCandleMapping):
    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def to_candle(self, database_candle: SqliteCandle) -> Candle:
        with Session(self._engine) as session:
            exchange = ta.get_exchange(database_candle.exchange_id, session)
            market = ta.get_market(database_candle.market_id, session)
            resolution = ta.get_resolution(database_candle.resolution_id, session)

        assert exchange, "Exchange must be set in the database."
        assert market, "Market must be set in the database."
        assert resolution, "Resolution must be set in the database."

        return Candle(
            id=database_candle.id,
            exchange=exchange,
            market=market,
            resolution=resolution,
            started_at=database_candle.started_at,
            open=Decimal(database_candle.open),
            high=Decimal(database_candle.high),
            low=Decimal(database_candle.low),
            close=Decimal(database_candle.close),
            base_token_volume=Decimal(database_candle.base_token_volume),
            trades=database_candle.trades,
            usd_volume=Decimal(database_candle.usd_volume),
            starting_open_interest=Decimal(database_candle.starting_open_interest),
        )

    def to_database_candle(self, candle: Candle) -> SqliteCandle:
        with Session(self._engine) as session:
            exchange_id = ta.get_exchange_id(candle.exchange, session)
            sql_market = ta.get_market_id(candle.market, session)
            sql_resolution = ta.get_resolution_id(candle.resolution, session)

        return SqliteCandle(
            id=candle.id,
            exchange_id=exchange_id,
            market_id=sql_market,
            resolution_id=sql_resolution,
            started_at=candle.started_at,
            open=str(candle.open),
            high=str(candle.high),
            low=str(candle.low),
            close=str(candle.close),
            base_token_volume=str(candle.base_token_volume),
            trades=candle.trades,
            usd_volume=str(candle.usd_volume),
            starting_open_interest=str(candle.starting_open_interest),
        )
