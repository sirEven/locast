from typing import List
from sqlalchemy import Engine
from sqlmodel import Session

from locast.candle.candle import Candle
from locast.candle_storage.database_candle_mapper import DatabaseCandleMapper
from locast.candle_storage.database_type import DatabaseType


def store_candles(
    database: DatabaseType,
    candles: List[Candle],
    engine: Engine,
) -> None:
    with Session(engine) as session:
        for candle in candles:
            session.add(DatabaseCandleMapper.to_database_candle(database, candle))
        session.commit()
