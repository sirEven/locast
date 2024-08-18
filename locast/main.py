import asyncio
from typing import List

from sqlmodel import create_engine

from sir_utilities.date_time import string_to_datetime

from locast.candle.candle import Candle
from locast.candle.candle_utility import CandleUtility as cu
from locast.candle.exchange_candle_mapper import ExchangeCandleMapper
from locast.candle.dydx.dydx_resolution import DydxResolution
from locast.candle.exchange import Exchange
from locast.candle_storage.sql.sqlite_candle_storage import SqliteCandleStorage
from locast.candle_storage.sql.setup_database import create_db_and_tables
from tests.helper.candle_mockery.mock_dydx_v4_candle_dicts import (
    mock_dydx_v4_candle_dict_batch,
)


async def main() -> None:
    exchange = Exchange.DYDX_V4
    resolution = DydxResolution.ONE_MINUTE.seconds
    market = "ETH-USD"
    start_str = "2024-01-01T00:00:00+00:00"
    end_str = "2024-01-02T00:00:00+00:00"

    start = string_to_datetime(start_str)
    end = string_to_datetime(end_str)
    amount = cu.amount_of_candles_in_range(start, end, resolution)
    eth_dicts = mock_dydx_v4_candle_dict_batch(
        DydxResolution.ONE_MINUTE.notation,
        market,
        start_str,
        end_str,
        batch_size=amount,
    )

    print(f"Expected Amount: {amount}.")
    candles: List[Candle] = ExchangeCandleMapper.to_candles(exchange, eth_dicts)
    print(f"Mocked Amount: {len(candles)}.")

    sqlite_file_name = "candles.db"
    sqlite_url = f"sqlite:///{sqlite_file_name}"
    engine = create_engine(sqlite_url, echo=False)

    candle_storage = SqliteCandleStorage(engine)

    create_db_and_tables(engine)

    await candle_storage.store_candles(candles)
    await asyncio.sleep(5)
    candles = await candle_storage.retrieve_candles(
        exchange,
        market,
        resolution,
    )

    print(
        f"Candles store from {candles[-1].started_at}, to: {candles[0].started_at}, Amount: {len(candles)}."
    )


asyncio.run(main())
