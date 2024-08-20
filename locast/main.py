import asyncio
import time
from typing import List

from sir_utilities.date_time import string_to_datetime

from locast.candle.candle import Candle
from locast.candle.candle_utility import CandleUtility as cu
from locast.candle.exchange_candle_mapper import ExchangeCandleMapper
from locast.candle.dydx.dydx_resolution import DydxResolution
from locast.candle.exchange import Exchange
from locast.candle_storage.sql.sqlite_candle_storage import SqliteCandleStorage
from tests.helper.candle_mockery.mock_dydx_v4_candle_dicts import (
    mock_dydx_v4_candle_dict_batch,
)


async def main() -> None:
    exchange = Exchange.DYDX_V4
    resolution = DydxResolution.ONE_MINUTE.seconds
    market = "ETH-USD"
    start_str = "2024-01-01T00:00:00+00:00"
    end_str = "2024-01-31T00:00:00+00:00"

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

    candles: List[Candle] = ExchangeCandleMapper.to_candles(exchange, eth_dicts)

    print(f"Expected Amount: {amount}.")
    print(f"Mocked Amount: {len(candles)}.")

    candle_storage = SqliteCandleStorage()

    start_time = time.time()
    await candle_storage.store_candles(candles)
    print(f"STORING DONE ({round(time.time()-start_time,2)} seconds).")

    start_time = time.time()
    retrieved_candles = await candle_storage.retrieve_candles(
        exchange,
        market,
        resolution,
    )
    print(f"RETRIEVING DONE ({round(time.time()-start_time,2)} seconds).")
    if len(retrieved_candles) > 0:
        print(
            f"Candles stored from {retrieved_candles[-1].started_at}, to: {retrieved_candles[0].started_at}, Amount: {len(retrieved_candles)}."
        )
    else:
        print(f"Candles: {retrieved_candles}")


asyncio.run(main())
