from datetime import datetime
from typing import List, Protocol

from locast.candle.candle import Candle


class APIFetcher(Protocol):
    async def fetch(
        self,
        market: str,
        resolution: str,
        start_date: datetime,
        end_date: datetime,
    ) -> List[Candle]: ...
