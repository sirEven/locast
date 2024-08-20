from typing import List, Dict, Any
from locast.candle.candle import Candle
from locast.candle.exchange_candle_mapping import ExchangeCandleMapping


class ExchangeCandleMapper:
    """
    A class that maps candle dictionaries from different exchanges to Candle objects.
    Note: _to_candle() exists, to extract the _select_mapping() call outside of the for loop
    in to_candles(), in order to only have it run every batch instead of every candle.
    """

    def __init__(self, mapping: ExchangeCandleMapping) -> None:
        self._mapping = mapping

    def to_candles(self, candle_dicts: List[Dict[str, Any]]) -> List[Candle]:
        return [
            self._to_candle(self._mapping, candle_dict) for candle_dict in candle_dicts
        ]

    def to_candle(self, candle_dict: Dict[str, Any]) -> Candle:
        return self._to_candle(self._mapping, candle_dict)

    def _to_candle(
        self,
        mapping: ExchangeCandleMapping,
        candle_dict: Dict[str, Any],
    ) -> Candle:
        return mapping.to_candle(candle_dict)
