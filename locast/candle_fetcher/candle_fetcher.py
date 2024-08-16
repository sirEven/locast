from datetime import datetime
from typing import Protocol, List

from locast.candle.candle import Candle


class CandleFetcher(Protocol):
    async def fetch_candles(
        self,
        market: str,
        resolution: str,
        start_date: datetime,
        end_date: datetime,
    ) -> List[Candle]: ...

    async def fetch_candles_up_to_now(
        self,
        market: str,
        resolution: str,
        start_date: datetime,
    ) -> List[Candle]: ...
