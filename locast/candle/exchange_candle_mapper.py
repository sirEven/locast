from typing import List, Dict, Any
from locast.candle.candle import Candle
from locast.candle.dydx.dydx_candle_mapping import (
    DydxV3CandleMapping,
    DydxV4CandleMapping,
)
from locast.candle.exchange import Exchange


class ExchangeCandleMapper:
    """
    A class that maps candle dictionaries from different exchanges to Candle objects.
    """

    mappings = {
        Exchange.DYDX: DydxV3CandleMapping(),
        Exchange.DYDX_V4: DydxV4CandleMapping(),
    }

    @staticmethod
    def to_candles(
        exchange: Exchange,
        candle_dicts: List[Dict[str, Any]],
    ) -> List[Candle]:
        return [
            ExchangeCandleMapper.to_candle(exchange, candle_dict)
            for candle_dict in candle_dicts
        ]

    @staticmethod
    def to_candle(exchange: Exchange, candle_dict: Dict[str, Any]) -> Candle:
        if not (mapping := ExchangeCandleMapper.mappings.get(exchange)):
            raise ValueError(
                f"Candle can't be mapped for unknown exchange: {exchange}."
            )

        return mapping.to_candle(candle_dict)
