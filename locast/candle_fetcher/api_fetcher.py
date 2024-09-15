from datetime import datetime
from typing import List, Protocol

from locast.candle.candle import Candle
from locast.candle.exchange import Exchange
from locast.candle.resolution import ResolutionDetail


class APIFetcher(Protocol):
    @property
    def exchange(self) -> Exchange: ...
    async def fetch(
        self,
        market: str,
        resolution: ResolutionDetail,
        start_date: datetime,
        end_date: datetime,
    ) -> List[Candle]: ...
