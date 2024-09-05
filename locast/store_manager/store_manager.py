from datetime import datetime
from typing import List
from locast.candle.candle import Candle
from locast.candle.exchange import Exchange
from locast.candle.resolution import ResolutionDetail, Seconds
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
        market: str,
        resolution: ResolutionDetail,
        start_date: datetime,
        replace_existing_cluster: bool = False,
    ) -> None:
        # 1) Check if cluster exists in candle store
        cluster_info = await self._candle_storage.get_cluster_info(
            self._candle_fetcher.exchange,
            market,
            resolution.seconds,
        )

        if cluster_info:
            if not replace_existing_cluster:
                raise ExistingClusterException(
                    f"Cluster already exists for market {market} and resolution {resolution}."
                )

            await self.delete_cluster(
                self._candle_fetcher.exchange,
                market,
                resolution.seconds,
            )

        cluster = await self._candle_fetcher.fetch_candles_up_to_now(
            market,
            resolution,
            start_date,
        )

        await self._candle_storage.store_candles(cluster)

    # WIP: CONTINUE - write tests create_cluster()
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
