import asyncio
import time
from typing import List

from sir_utilities.date_time import string_to_datetime
from sqlalchemy import create_engine

from locast.candle.candle import Candle
from locast.candle.candle_utility import CandleUtility as cu
from locast.candle.dydx.dydx_candle_mapping import DydxV4CandleMapping
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
    start_str = "2024-02-01T00:00:00+00:00"
    end_str = "2024-02-25T00:00:00+00:00"

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
    v4_mapper = ExchangeCandleMapper(DydxV4CandleMapping())
    candles: List[Candle] = v4_mapper.to_candles(eth_dicts)

    # print(f"Expected Amount: {amount}.")
    print(f"Mocked Amount: {len(candles)}.")

    engine = create_engine("sqlite:///locast.db", echo=False)
    candle_storage = SqliteCandleStorage(engine)

    start_time = time.time()
    await candle_storage.store_candles(candles)
    print(
        f"Time to store {len(candles)} candles: ({round(time.time()-start_time,2)} seconds)."
    )

    start_time = time.time()
    retrieved_candles = await candle_storage.retrieve_candles(
        exchange,
        market,
        resolution,
    )
    print(
        f"Time to retrieve {len(retrieved_candles)} candles: ({round(time.time()-start_time,2)} seconds)."
    )
    if len(retrieved_candles) > 0:
        print(
            f"Candles retrieved from {retrieved_candles[-1].started_at}, to: {retrieved_candles[0].started_at}."
        )
    else:
        print(f"Candles: {retrieved_candles}")

    cluster_info = await candle_storage.get_cluster_info(exchange, market, resolution)
    if cluster_info:
        print(cluster_info)


asyncio.run(main())
