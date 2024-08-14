from typing import List
from sqlalchemy import Engine
from sqlmodel import Session

from locast.candle.candle import Candle
from locast.candle_storage.sql.model_mapping import ModelMapping


def store_candles(candles: List[Candle], engine: Engine) -> None:
    with Session(engine) as session:
        for candle in candles:
            session.add(ModelMapping.to_sqlite_candle(candle))

        session.commit()
