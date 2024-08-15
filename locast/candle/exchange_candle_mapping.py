from typing import Any, Dict, Protocol

from locast.candle.candle import Candle


class ExchangeCandleMapping(Protocol):
    def to_candle(self, exchange_representation: Dict[str, Any]) -> Candle: ...
