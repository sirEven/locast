from datetime import datetime
from typing import Dict, List

from locast.candle.candle_utility import CandleUtility as cu
from locast.candle.candle import Candle
from locast.candle.exchange import Exchange
from locast.candle.exchange_resolution import ResolutionDetail
from locast.candle_fetcher.candle_fetcher import CandleFetcher
from locast.candle_storage.cluster_info import ClusterInfo
from locast.candle_storage.candle_storage import CandleStorage
from locast.logging_functions import (
    log_redundant_call,
    log_start_date_shifted_to_horizon,
)

# TODO: Expand API by adding convenience methods such as def retrieve_segment(from, to, exchange, market, resolution) -> List[Candle]: ...


class StoreManager:
    def __init__(
        self,
        candle_fetcher: CandleFetcher,
        candle_storage: CandleStorage,
    ) -> None:
        self._candle_fetcher = candle_fetcher
        self._candle_storage = candle_storage

        self._horizon_cache: Dict[str, datetime] = {}

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

        start_date = await self._check_horizon(market, resolution, start_date)

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

        if cluster_info.size == 0:
            raise MissingClusterException(
                f"Cluster does not exist for market {market} and resolution {resolution.notation}."
            )

        return await self._candle_storage.retrieve_cluster(exchange, market, resolution)

    async def retrieve_newest_candles(
        self,
        exchange: Exchange,
        market: str,
        resolution: ResolutionDetail,
        amount: int,
    ) -> List[Candle]:
        cluster_info = await self.get_cluster_info(exchange, market, resolution)

        if cluster_info.size == 0:
            raise MissingClusterException(
                f"Cluster does not exist for market {market} and resolution {resolution.notation}."
            )

        amount_to_retrieve = min(amount, cluster_info.size)

        return await self._candle_storage.retrieve_newest_candles(
            exchange,
            market,
            resolution,
            amount_to_retrieve,
        )

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

    async def _check_horizon(
        self,
        market: str,
        resolution: ResolutionDetail,
        start_date: datetime,
    ) -> datetime:
        if not (horizon := self._horizon_cache.get(f"{market}_{resolution.notation}")):
            horizon = await self._candle_fetcher.find_horizon(market, resolution)
            self._horizon_cache[f"{market}_{resolution.notation}"] = horizon

        if start_date < horizon:
            log_start_date_shifted_to_horizon(
                "⏭️",
                self._candle_fetcher.exchange,
                start_date,
                horizon,
            )
            start_date = horizon
        return start_date


class ExistingClusterException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class MissingClusterException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
