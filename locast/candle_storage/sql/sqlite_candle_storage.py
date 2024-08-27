from typing import List
from sqlalchemy import Engine
from sqlmodel import SQLModel, Session, select

from locast.candle.candle import Candle
from locast.candle.exchange import Exchange
from locast.candle.resolution import Seconds
from locast.candle_storage.candle_storage import CandleStorage
from locast.candle_storage.database_candle_mapper import DatabaseCandleMapper
from locast.candle_storage.sql.sqlite_candle_mapping import SqliteCandleMapping
from locast.candle_storage.sql.tables import SqliteCandle

from locast.candle_storage.sql.table_utility import TableUtility as tu


class SqliteCandleStorage(CandleStorage):
    def __init__(self, engine: Engine) -> None:
        self._engine = engine
        SQLModel.metadata.create_all(self._engine)

    async def store_candles(self, candles: List[Candle]) -> None:
        with Session(self._engine) as session:
            mapper = DatabaseCandleMapper(SqliteCandleMapping(session))
            for candle in candles:
                session.add(mapper.to_database_candle(candle))
            session.commit()

    async def retrieve_candles(
        self,
        exchange: Exchange,
        market: str,
        resolution: Seconds,
    ) -> List[Candle]:
        with Session(self._engine) as session:
            sql_exchange = tu.lookup_sql_exchange(exchange, session)
            sql_market = tu.lookup_or_create_sql_market(market, session)
            sql_resolution = tu.lookup_or_create_sql_resolution(resolution, session)

            assert sql_exchange, f"Exchange {exchange} not found in database."
            assert sql_market, f"Market {market} not found in database."
            assert sql_resolution, f"Resolution {resolution} not found in database."

            statement = select(SqliteCandle).where(
                (SqliteCandle.exchange_id == sql_exchange.id)
                & (SqliteCandle.market_id == sql_market.id)
                & (SqliteCandle.resolution_id == sql_resolution.id)
            )

            results = session.exec(statement)
            return self._to_candles(list(results.all()))

    def _to_candles(self, database_candles: List[SqliteCandle]) -> List[Candle]:
        mapper = DatabaseCandleMapper(SqliteCandleMapping())
        return [mapper.to_candle(sqlite_candle) for sqlite_candle in database_candles]
