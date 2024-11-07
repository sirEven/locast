from typing import List, Protocol

from locast.candle.candle import Candle
from locast.candle.exchange import Exchange
from locast.candle.exchange_resolution import ResolutionDetail
from locast.candle_storage.cluster_info import ClusterInfo


class CandleStorage(Protocol):
    async def store_candles(self, candles: List[Candle]) -> None: ...

    async def retrieve_cluster(
        self,
        exchange: Exchange,
        market: str,
        resolution: ResolutionDetail,
    ) -> List[Candle]: ...

    async def retrieve_newest_candles(
        self,
        exchange: Exchange,
        market: str,
        resolution: ResolutionDetail,
        amount: int,
    ) -> List[Candle]: ...

    async def delete_cluster(
        self,
        exchange: Exchange,
        market: str,
        resolution: ResolutionDetail,
    ) -> None: ...

    async def get_cluster_info(
        self,
        exchange: Exchange,
        market: str,
        resolution: ResolutionDetail,
    ) -> ClusterInfo: ...
