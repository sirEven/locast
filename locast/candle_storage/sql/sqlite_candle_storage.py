from typing import List
from sqlalchemy import Engine
from sqlmodel import Session

from locast.candle.candle import Candle
from locast.candle.exchange import Exchange
from locast.candle.resolution import Seconds
from locast.candle_storage.candle_storage import CandleStorage
from locast.candle_storage.database_candle_mapper import DatabaseCandleMapper
from locast.candle_storage.database_type import DatabaseType


class SqliteCandleStorage(CandleStorage):
    def __init__(self, engine: Engine) -> None:
        self._engine = engine
        self._database_type = DatabaseType.SQLITE

    async def store_candles(self, candles: List[Candle]) -> None:
        with Session(self._engine) as session:
            for candle in candles:
                session.add(
                    DatabaseCandleMapper.to_database_candle(
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
        raise NotImplementedError
