from typing import Any, Dict, Protocol

from locast.candle.candle import Candle


class CandleMapping(Protocol):
    def dict_to_candle(self, candle_dict: Dict[str, Any]) -> Candle: ...
