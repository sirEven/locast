from typing import List
from sqlalchemy import Engine
from sqlmodel import Session

from locast.candle.candle import Candle
from locast.candle_storage.sql.sqlite_candle_mapping import SqliteCandleMapping


def store_candles(candles: List[Candle], engine: Engine) -> None:
    mapping = SqliteCandleMapping()
    with Session(engine) as session:
        for candle in candles:
            session.add(mapping.to_sqlite_candle(candle))

        session.commit()
