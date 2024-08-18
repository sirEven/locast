from datetime import datetime
from typing import List
from locast.candle.candle import Candle
from locast.candle.exchange import Exchange
from locast.candle_fetcher.api_fetcher import APIFetcher


class DydxV3Fetcher(APIFetcher):
    def __init__(self) -> None:
        self._exchange = Exchange.DYDX

    @property
    def exchange(self) -> Exchange:
        return self._exchange
    
    async def fetch(
        self,
        market: str,
        resolution: str,
        start_date: datetime,
        end_date: datetime,
    ) -> List[Candle]:
        raise NotImplementedError