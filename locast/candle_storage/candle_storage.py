from typing import List, Protocol

from locast.candle.candle import Candle
from locast.candle.exchange import Exchange
from locast.candle.resolution import Seconds
from locast.candle_storage.cluster_info import ClusterInfo


class CandleStorage(Protocol):
    async def store_candles(self, candles: List[Candle]) -> None: ...

    async def retrieve_candles(
        self,
        exchange: Exchange,
        market: str,
        resolution: Seconds,
    ) -> List[Candle]: ...

    async def get_cluster_info(
        self,
        exchange: Exchange,
        market: str,
        resolution: Seconds,
    ) -> ClusterInfo | None: ...
