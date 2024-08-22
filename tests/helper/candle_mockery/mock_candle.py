from decimal import Decimal
from sir_utilities.date_time import string_to_datetime


from locast.candle.candle import Candle
from locast.candle.dydx.dydx_resolution import DydxResolution
from locast.candle.exchange import Exchange

from tests.helper.candle_mockery.base_values import copy_base_values


def mock_candle(exchange: Exchange) -> Candle:
    bv = copy_base_values()
    return Candle(
        None,
        exchange,
        bv["TICKER"],
        DydxResolution.notation_to_seconds(bv["RESOLUTION"]),
        string_to_datetime(bv["STARTED_AT"]),
        Decimal(bv["PRICE"]),
        Decimal(bv["PRICE"]),
        Decimal(bv["PRICE"]),
        Decimal(bv["PRICE"]),
        Decimal(bv["BASE_TOKEN_VOLUME"]),
        bv["TRADES"],
        Decimal(bv["USD_VOLUME"]),
        Decimal(bv["STARTING_OPEN_INTEREST"]),
    )
