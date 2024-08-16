import asyncio
from typing import List

from sqlmodel import create_engine

from locast.candle.candle import Candle
from locast.candle.dydx.dydx_candle_mapping import DydxV4CandleMapping
from locast.candle_storage.sql.sqlite_candle_storage import SqliteCandleStorage
from locast.candle_storage.sql.setup_database import create_db_and_tables


async def main():
    candle_dict = {
        "startedAt": "2024-04-01T09:59:00.000Z",
        "ticker": "ETH-USD",
        "resolution": "1MIN",
        "low": "3537.3",
        "high": "3540.9",
        "open": "3540.9",
        "close": "3537.3",
        "baseTokenVolume": "0.042",
        "usdVolume": "148.6422",
        "trades": 2,
        "startingOpenInterest": "934.027",
    }

    mapping = DydxV4CandleMapping()
    candles: List[Candle] = [mapping.to_candle(candle_dict) for _ in range(5)]

    sqlite_file_name = "candles.db"
    sqlite_url = f"sqlite:///{sqlite_file_name}"
    engine = create_engine(sqlite_url, echo=True)

    candle_storage = SqliteCandleStorage(engine)

    create_db_and_tables(engine)

    await candle_storage.store_candles(candles)


asyncio.run(main())
