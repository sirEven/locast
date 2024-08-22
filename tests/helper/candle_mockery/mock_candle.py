from decimal import Decimal
from sir_utilities.date_time import string_to_datetime


from locast.candle.candle import Candle
from locast.candle.dydx.dydx_resolution import DydxResolution
from locast.candle.exchange import Exchange

from tests.helper.candle_mockery.dydx_candle_dicts import (
    STARTED_AT,
    TICKER,
    RESOLUTION,
    PRICE,
    BASE_TOKEN_VOLUME,
    USD_VOLUME,
    TRADES,
    STARTING_OPEN_INTEREST,
)


def mock_candle(exchange: Exchange) -> Candle:
    return Candle(
        None,
        exchange,
        TICKER,
        DydxResolution.notation_to_seconds(RESOLUTION),
        string_to_datetime(STARTED_AT),
        Decimal(PRICE),
        Decimal(PRICE),
        Decimal(PRICE),
        Decimal(PRICE),
        Decimal(BASE_TOKEN_VOLUME),
        TRADES,
        Decimal(USD_VOLUME),
        Decimal(STARTING_OPEN_INTEREST),
    )
