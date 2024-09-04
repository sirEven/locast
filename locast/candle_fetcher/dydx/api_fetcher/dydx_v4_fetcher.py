from datetime import datetime
from typing import Any, Dict, List

from dydx_v4_client.indexer.rest.indexer_client import IndexerClient  # type: ignore
from dydx_v4_client.network import TESTNET  # type: ignore


from locast.candle.candle import Candle

from locast.candle.dydx.dydx_candle_mapping import DydxV4CandleMapping
from locast.candle.exchange_candle_mapper import ExchangeCandleMapper
from locast.candle.resolution import ResolutionDetail
from locast.candle_fetcher.api_fetcher import APIFetcher
from locast.candle_fetcher.dydx.api_fetcher.datetime_format import (
    datetime_to_dydx_iso_str,
)


class DydxV4Fetcher(APIFetcher):
    def __init__(
        self,
        client: IndexerClient = IndexerClient(TESTNET.rest_indexer),
    ) -> None:
        self._client = client
        self._mapper = ExchangeCandleMapper(DydxV4CandleMapping())

    async def fetch(
        self,
        market: str,
        resolution: ResolutionDetail,
        start_date: datetime,
        end_date: datetime,
    ) -> List[Candle]:
        response: Dict[
            str,
            Any,
        ] = await self._client.markets.get_perpetual_market_candles(  # type: ignore
            market=market,
            resolution=resolution.notation,
            from_iso=datetime_to_dydx_iso_str(start_date),
            to_iso=datetime_to_dydx_iso_str(end_date),
        )
        assert response["candles"]
        return self._mapper.to_candles(response["candles"])
