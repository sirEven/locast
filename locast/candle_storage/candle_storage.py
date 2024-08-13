from typing import List, Protocol

from locast.candle.candle import Candle
from locast.candle.exchange import Exchange
from locast.candle.resolution import Seconds


class CandleStorage(Protocol):
    async def store_candles(self, candles: List[Candle]) -> None: ...

    async def retrieve_candles(
        self,
        exchange: Exchange,
        market: str,
        resolution: Seconds,
    ) -> List[Candle]: ...
