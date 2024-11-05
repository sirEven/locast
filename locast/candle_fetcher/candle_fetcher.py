from datetime import datetime
from typing import Protocol, List, runtime_checkable

from locast.candle.candle import Candle
from locast.candle.exchange import Exchange
from locast.candle.exchange_resolution import ResolutionDetail


@runtime_checkable
class CandleFetcher(Protocol):
    @property
    def exchange(self) -> Exchange: ...

    @property
    def log_progress(self) -> bool: ...

    @log_progress.setter
    def log_progress(self, value: bool) -> None: ...

    async def fetch_candles(
        self,
        market: str,
        resolution: ResolutionDetail,
        start_date: datetime,
        end_date: datetime,
    ) -> List[Candle]: ...

    async def fetch_candles_up_to_now(
        self,
        market: str,
        resolution: ResolutionDetail,
        start_date: datetime,
    ) -> List[Candle]: ...

    async def find_horizon(
        self,
        market: str,
        resolution: ResolutionDetail,
    ) -> datetime: ...
