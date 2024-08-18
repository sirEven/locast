from typing import List
from locast.candle.candle import Candle
from locast.candle.exchange import Exchange
from locast.candle.resolution import Seconds
from locast.candle_fetcher.candle_fetcher import CandleFetcher
from locast.candle_storage.candle_storage import CandleStorage


class StoreManager:
    def __init__(
        self,
        candle_fetcher: CandleFetcher,
        candle_storage: CandleStorage,
    ) -> None:
        self._candle_fetcher = candle_fetcher
        self._candle_storage = candle_storage

    async def create_cluster(self) -> None:
        raise NotImplementedError

    async def update_cluster(self) -> None:
        raise NotImplementedError

    async def retrieve_cluster(
        self,
        exchange: Exchange,
        market: str,
        resolution: Seconds,
    ) -> List[Candle]:
        raise NotImplementedError
