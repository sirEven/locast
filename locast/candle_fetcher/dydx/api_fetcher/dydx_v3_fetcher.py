from datetime import datetime
from typing import List
from locast.candle.candle import Candle
from locast.candle.resolution import ResolutionDetail
from locast.candle_fetcher.api_fetcher import APIFetcher


class DydxV3Fetcher(APIFetcher):
    async def fetch(
        self,
        market: str,
        resolution: ResolutionDetail,
        start_date: datetime,
        end_date: datetime,
    ) -> List[Candle]:
        raise NotImplementedError
