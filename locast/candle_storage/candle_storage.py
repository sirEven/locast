from typing import List, Protocol

from locast.candle.candle import Candle


class CandleStorage(Protocol):
    async def store_candles(self, candles: List[Candle]) -> None: ...