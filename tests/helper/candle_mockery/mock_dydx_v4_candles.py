from datetime import datetime, timedelta
from typing import List

from sir_utilities.date_time import datetime_to_string

from locast.candle.candle_utility import CandleUtility as cu
from locast.candle.candle import Candle
from locast.candle.dydx.dydx_candle_mapping import DydxV4CandleMapping
from locast.candle.exchange import Exchange
from locast.candle.exchange_candle_mapper import ExchangeCandleMapper
from locast.candle.resolution import ResolutionDetail
from tests.helper.candle_mockery.mock_dydx_v4_candle_dicts import (
    mock_dydx_v4_candle_dict_batch,
)


def mock_dydx_v4_candle_range(
    market: str,
    resolution: ResolutionDetail,
    start_date: datetime,
    end_date: datetime,
) -> List[Candle]:
    amount = cu.amount_of_candles_in_range(start_date, end_date, resolution)

    mock_candle_dicts = mock_dydx_v4_candle_dict_batch(
        Exchange.DYDX_V4,
        resolution.notation,
        market,
        datetime_to_string(start_date),
        datetime_to_string(end_date),
        batch_size=amount,
    )

    mapper = ExchangeCandleMapper(DydxV4CandleMapping())

    return mapper.to_candles(mock_candle_dicts)


def mock_dydx_v4_candles(
    market: str,
    resolution: ResolutionDetail,
    amount: int,
    start_date: datetime,
) -> List[Candle]:
    end_date = start_date + timedelta(seconds=resolution.seconds * amount)

    mock_candle_dicts = mock_dydx_v4_candle_dict_batch(
        Exchange.DYDX_V4,
        resolution.notation,
        market,
        datetime_to_string(start_date),
        datetime_to_string(end_date),
        batch_size=amount,
    )

    mapper = ExchangeCandleMapper(DydxV4CandleMapping())

    return mapper.to_candles(mock_candle_dicts)
