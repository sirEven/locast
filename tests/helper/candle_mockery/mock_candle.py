from decimal import Decimal
from sir_utilities.date_time import string_to_datetime


from locast.candle.candle import Candle
from locast.candle.exchange import Exchange

from locast.candle.exchange_resolution import ResolutionDetail
from tests.helper.candle_mockery.base_values import copy_base_values


def mock_candle(exchange: Exchange) -> Candle:
    bv = copy_base_values()
    return Candle(
        id=None,
        exchange=exchange,
        market=bv["TICKER"],
        resolution=ResolutionDetail(
            bv["RESOLUTION"]["seconds"],
            bv["RESOLUTION"]["notation"],
        ),
        started_at=string_to_datetime(bv["STARTED_AT"]),
        open=Decimal(bv["PRICE"]),
        high=Decimal(bv["PRICE"]),
        low=Decimal(bv["PRICE"]),
        close=Decimal(bv["PRICE"]),
        base_token_volume=Decimal(bv["BASE_TOKEN_VOLUME"]),
        trades=bv["TRADES"],
        usd_volume=Decimal(bv["USD_VOLUME"]),
        starting_open_interest=Decimal(bv["STARTING_OPEN_INTEREST"]),
    )
