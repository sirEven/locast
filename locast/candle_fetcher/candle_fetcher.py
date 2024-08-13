from datetime import datetime
from typing import Protocol, List

from locast.candle.candle import Candle
from locast.candle.exchange import Exchange


class CandleFetcher(Protocol):
    async def fetch_candles(
        self,
        exchange: Exchange,
        market: str,
        resolution: str,
        start_date: datetime,
        end_date: datetime,
    ) -> List[Candle]: ...

    async def fetch_candles_up_to_now(
        self,
        exchange: Exchange,
        market: str,
        resolution: str,
        start_date: datetime,
    ) -> List[Candle]: ...