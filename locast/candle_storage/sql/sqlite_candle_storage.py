from typing import List
from sqlmodel import SQLModel, Session, select, create_engine

from locast.candle.candle import Candle
from locast.candle.exchange import Exchange
from locast.candle.resolution import Seconds
from locast.candle_storage.candle_storage import CandleStorage
from locast.candle_storage.database_candle_mapper import DatabaseCandleMapper
from locast.candle_storage.sql.sqlite_candle_mapping import SqliteCandleMapping
from locast.candle_storage.sql.tables import SqliteCandle

from locast.candle_storage.sql.table_utility import TableAccess as ta


class SqliteCandleStorage(CandleStorage):
    def __init__(self, sqlite_url: str = "sqlite:///locast.db") -> None:
        self._engine = create_engine(sqlite_url, echo=False)
        self._db_candle_mapper = DatabaseCandleMapper(SqliteCandleMapping(self._engine))

        SQLModel.metadata.create_all(self._engine)

    # TODO: Implement UNIQUE constraint on combo (exchange, market, resolution, startedAt)
    async def store_candles(self, candles: List[Candle]) -> None:
        with Session(self._engine) as session:
            for candle in candles:
                session.add(self._db_candle_mapper.to_database_candle(candle))
            session.commit()

    async def retrieve_candles(
        self,
        exchange: Exchange,
        market: str,
        resolution: Seconds,
    ) -> List[Candle]:
        with Session(self._engine) as session:
            statement = select(SqliteCandle).where(
                SqliteCandle.exchange_id == ta.get_exchange_id(exchange, session),
                SqliteCandle.market_id == ta.get_market_id(market, session),
                SqliteCandle.resolution_id == ta.get_resolution_id(resolution, session),
            )
            results = session.exec(statement)
            return self._to_candles(list(results.all()))

    def _to_candles(self, database_candles: List[SqliteCandle]) -> List[Candle]:
        return [
            self._db_candle_mapper.to_candle(sqlite_candle)
            for sqlite_candle in database_candles
        ]
