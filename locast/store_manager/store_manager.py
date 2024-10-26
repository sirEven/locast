from datetime import datetime
from typing import List

from locast.candle.candle_utility import CandleUtility as cu
from locast.candle.candle import Candle
from locast.candle.exchange import Exchange
from locast.candle.exchange_resolution import ResolutionDetail
from locast.candle_fetcher.candle_fetcher import CandleFetcher
from locast.candle_storage.cluster_info import ClusterInfo
from locast.candle_storage.candle_storage import CandleStorage
from locast.logging import log_redundant_call


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
        cluster_info = await self.get_cluster_info(
            self._candle_fetcher.exchange,
            market,
            resolution,
        )

        if cluster_info.newest_candle:
            if not replace_existing_cluster:
                raise ExistingClusterException(
                    f"Cluster already exists for market {market} and resolution {resolution.notation}."
                )

            await self.delete_cluster(
                self._candle_fetcher.exchange,
                market,
                resolution,
            )

        cluster = await self._candle_fetcher.fetch_candles_up_to_now(
            market,
            resolution,
            start_date,
        )

        await self._candle_storage.store_candles(cluster)

    async def retrieve_cluster(
        self,
        exchange: Exchange,
        market: str,
        resolution: ResolutionDetail,
    ) -> List[Candle]:
        cluster_info = await self.get_cluster_info(exchange, market, resolution)

        if not cluster_info.newest_candle:
            raise MissingClusterException(
                f"Cluster does not exist for market {market} and resolution {resolution.notation}."
            )

        return await self._candle_storage.retrieve_cluster(exchange, market, resolution)

    async def update_cluster(
        self,
        exchange: Exchange,
        market: str,
        resolution: ResolutionDetail,
    ) -> None:
        cluster_info = await self.get_cluster_info(exchange, market, resolution)

        if cluster_info.is_uptodate:
            next_tick = cu.next_tick(resolution)
            msg = f"Cluster is already up to date. Try again after {next_tick}."
            log_redundant_call("♻️", msg)
            return

        if not (head := cluster_info.newest_candle):
            raise MissingClusterException(
                f"Cluster does not exist for market {market} and resolution {resolution.notation}."
            )

        start_date = cu.add_one_resolution(head.started_at, resolution)
        new_candles = await self._candle_fetcher.fetch_candles_up_to_now(
            market,
            resolution,
            start_date,
        )

        await self._candle_storage.store_candles(new_candles)

    async def delete_cluster(
        self,
        exchange: Exchange,
        market: str,
        resolution: ResolutionDetail,
    ) -> None:
        cluster_info = await self.get_cluster_info(exchange, market, resolution)

        if not cluster_info.newest_candle:
            raise MissingClusterException(
                f"Cluster does not exist for market {market} and resolution {resolution.notation}."
            )

        await self._candle_storage.delete_cluster(
            exchange,
            market,
            resolution,
        )

    async def get_cluster_info(
        self,
        exchange: Exchange,
        market: str,
        resolution: ResolutionDetail,
    ) -> ClusterInfo:
        return await self._candle_storage.get_cluster_info(exchange, market, resolution)

    # TODO: Expand API by adding convenience methods such as def retrieve_segment(from, to, exchange, market, resolution) -> List[Candle]: ...


class ExistingClusterException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class MissingClusterException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
