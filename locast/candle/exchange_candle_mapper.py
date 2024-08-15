from typing import List, Dict, Any
from locast.candle.candle import Candle
from locast.candle.dydx.dydx_candle_mapping import (
    DydxV3CandleMapping,
    DydxV4CandleMapping,
)
from locast.candle.exchange import Exchange
from locast.candle.exchange_candle_mapping import ExchangeCandleMapping


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
        mapping = ExchangeCandleMapper._select_mapping(exchange)
        return [
            ExchangeCandleMapper._to_candle(mapping, candle_dict)
            for candle_dict in candle_dicts
        ]

    @staticmethod
    def to_candle(
        exchange: Exchange,
        candle_dict: Dict[str, Any],
    ) -> Candle:
        mapping = ExchangeCandleMapper._select_mapping(exchange)
        return mapping.to_candle(candle_dict)

    @staticmethod
    def _to_candle(
        mapping: ExchangeCandleMapping,
        candle_dict: Dict[str, Any],
    ) -> Candle:
        return mapping.to_candle(candle_dict)

    @staticmethod
    def _select_mapping(exchange: Exchange) -> ExchangeCandleMapping:
        if not (mapping := ExchangeCandleMapper.mappings.get(exchange)):
            raise ValueError(
                f"Candle can't be mapped for unknown exchange: {exchange}."
            )
        return mapping
