from typing import Any, Dict, Protocol

from locast.candle.candle import Candle


class ExchangeCandleMapping(Protocol):
    def to_candle(self, exchange_candle: Dict[str, Any]) -> Candle: ...
