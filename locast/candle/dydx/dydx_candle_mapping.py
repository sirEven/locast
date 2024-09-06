from decimal import Decimal
from typing import Any, Dict
from locast.candle.candle import Candle
from locast.candle.exchange_candle_mapping import ExchangeCandleMapping
from locast.candle.dydx.dydx_resolution import DydxResolution


from sir_utilities.date_time import string_to_datetime

from locast.candle.exchange import Exchange


class DydxV4CandleMapping(ExchangeCandleMapping):
    def to_candle(self, exchange_candle: Dict[str, Any]) -> Candle:
        try:
            started_at = string_to_datetime(exchange_candle["startedAt"])
            market = exchange_candle["ticker"]
            resolution = DydxResolution.notation_to_resolution_detail(
                exchange_candle["resolution"]
            )
            p_low = Decimal(exchange_candle["low"])
            p_high = Decimal(exchange_candle["high"])
            p_open = Decimal(exchange_candle["open"])
            p_close = Decimal(exchange_candle["close"])
            base_token_volume = Decimal(exchange_candle["baseTokenVolume"])
            usd_volume = Decimal(exchange_candle["usdVolume"])
            trades = int(exchange_candle["trades"])
            starting_open_interest = Decimal(exchange_candle["startingOpenInterest"])

            return Candle(
                id=None,
                exchange=Exchange.DYDX_V4,
                started_at=started_at,
                market=market,
                resolution=resolution,
                low=p_low,
                high=p_high,
                open=p_open,
                close=p_close,
                base_token_volume=base_token_volume,
                usd_volume=usd_volume,
                trades=trades,
                starting_open_interest=starting_open_interest,
            )
        except Exception as e:
            raise ValueError(f"Error converting dict to Candle: {str(e)}") from e


class DydxV3CandleMapping(ExchangeCandleMapping):
    def to_candle(self, exchange_candle: Dict[str, Any]) -> Candle:
        try:
            started_at = string_to_datetime(exchange_candle["startedAt"])
            market = exchange_candle["market"]
            resolution = DydxResolution.notation_to_resolution_detail(
                exchange_candle["resolution"]
            )
            p_low = Decimal(exchange_candle["low"])
            p_high = Decimal(exchange_candle["high"])
            p_open = Decimal(exchange_candle["open"])
            p_close = Decimal(exchange_candle["close"])
            base_token_volume = Decimal(exchange_candle["baseTokenVolume"])
            trades = int(exchange_candle["trades"])
            usd_volume = Decimal(exchange_candle["usdVolume"])
            starting_open_interest = Decimal(exchange_candle["startingOpenInterest"])

            return Candle(
                id=None,
                exchange=Exchange.DYDX,
                market=market,
                resolution=resolution,
                started_at=started_at,
                open=p_open,
                high=p_high,
                low=p_low,
                close=p_close,
                base_token_volume=base_token_volume,
                trades=trades,
                usd_volume=usd_volume,
                starting_open_interest=starting_open_interest,
            )
        except Exception as e:
            raise ValueError(f"Error converting dict to Candle: {str(e)}") from e
