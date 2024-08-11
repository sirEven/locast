from typing import List, Protocol

from locast.candle.candle import Candle
from locast.candle.exchange import Exchange


class APIFetcher(Protocol):
    @property
    def exchange(self) -> Exchange: ...
    async def fetch(
        self,
        market: str,
        resolution: str,
        start_date: str,
        end_date: str,
    ) -> List[Candle]: ...