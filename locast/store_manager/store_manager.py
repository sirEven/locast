from datetime import datetime
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

    async def create_cluster(
        self,
        exchange: Exchange,
        market: str,
        resolution: Seconds,
        start_date: datetime,
    ) -> None:
        # TODO: If cluster already exists, throw exception
        raise NotImplementedError

    async def retrieve_cluster(
        self,
        exchange: Exchange,
        market: str,
        resolution: Seconds,
    ) -> List[Candle]:
        raise NotImplementedError

    async def update_cluster(
        self,
        exchange: Exchange,
        market: str,
        resolution: Seconds,
    ) -> List[Candle]:
        # TODO: If cluster does not exist, throw exception
        raise NotImplementedError

    async def delete_cluster(
        self,
        exchange: Exchange,
        market: str,
        resolution: Seconds,
    ) -> None:
        # TODO: If cluster does not exist, throw exception
        raise NotImplementedError


class ExistingClusterException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class MissingClusterException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
