import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any

from dydx3 import Client  # type: ignore

from locast.candle.candle import Candle
from locast.candle.exchange import Exchange
from locast.candle.resolution import ResolutionDetail
from locast.candle_fetcher.api_fetcher import APIFetcher
from locast.candle.exchange_candle_mapper import ExchangeCandleMapper
from locast.candle.dydx.dydx_candle_mapping import DydxV3CandleMapping
from locast.candle.candle_utility import CandleUtility as cu
from locast.candle_fetcher.dydx.api_fetcher.datetime_format import (
    datetime_to_dydx_iso_str,
)


class DydxV3Fetcher(APIFetcher):
    def __init__(self, client: Client, rate_throttle_sec: float = 0.4) -> None:
        self._exchange = Exchange.DYDX
        self._client = client
        self._mapper = ExchangeCandleMapper(DydxV3CandleMapping())

        self._throttle_rate = rate_throttle_sec
        self._last_request_time = datetime.min

    @property
    def exchange(self) -> Exchange:
        return self._exchange

    async def fetch(
        self,
        market: str,
        resolution: ResolutionDetail,
        start_date: datetime,
        end_date: datetime,
    ) -> List[Candle]:
        # NOTE: If only one candle is requested this prevents black magic in v3 backend
        if cu.amount_of_candles_in_range(start_date, end_date, resolution) == 1:
            start_date -= timedelta(seconds=1)

        now = datetime.now()
        time_since_last_request = (now - self._last_request_time).total_seconds()

        if time_since_last_request < self._throttle_rate:
            await asyncio.sleep(self._throttle_rate - time_since_last_request)

        loop = asyncio.get_running_loop()
        response: Dict[str, Any] = await loop.run_in_executor(
            None,
            lambda: self._client.public.get_candles(  # type: ignore
                market,
                resolution.notation,
                from_iso=datetime_to_dydx_iso_str(start_date),
                to_iso=datetime_to_dydx_iso_str(end_date),
            ).data,
        )

        self._last_request_time = datetime.now()
        return self._mapper.to_candles(response["candles"])  # type: ignore
