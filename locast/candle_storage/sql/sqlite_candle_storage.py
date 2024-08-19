from typing import List
from sqlalchemy import Engine
from sqlmodel import Session, select

from locast.candle.candle import Candle
from locast.candle.exchange import Exchange
from locast.candle.resolution import Seconds
from locast.candle_storage.candle_storage import CandleStorage
from locast.candle_storage.database_candle_mapper import DatabaseCandleMapper
from locast.candle_storage.database_type import DatabaseType
from locast.candle_storage.sql.tables import SqliteCandle

from locast.candle_storage.sql.table_utility import TableAccess as ta

# NOTE: Maybe utilize session refresh magic from sqlmodel in glue code when creating / updating a cluster freshly and wanting to pass the data on to next
# glued component such as model training, in order to save additional db calls by hand. But ideally, i think we will just separate the glued components in
# in a way, that each has its own database communication set up. So model training (or who ever) will load required data out of db by itself.


class SqliteCandleStorage(CandleStorage):
    def __init__(self, engine: Engine) -> None:
        self._engine = engine
        self._mapper = DatabaseCandleMapper(engine)
        self._database_type = DatabaseType.SQLITE

    # TODO: Implement UNIQUE constraint on combo (exchange, market, resolution, startedAt)
    # TODO: Normalize DB tables -> Exchange, Resolution, Market shall make up their own tables...
    async def store_candles(self, candles: List[Candle]) -> None:
        with Session(self._engine) as session:
            for candle in candles:
                session.add(
                    self._mapper.to_database_candle(
                        self._database_type,
                        candle,
                    )
                )
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
            self._mapper.to_candle(self._database_type, sqlite_candle)
            for sqlite_candle in database_candles
        ]
