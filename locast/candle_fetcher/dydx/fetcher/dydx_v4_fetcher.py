from datetime import datetime
from typing import Any, Dict, List

from dydx_v4_client.indexer.rest.indexer_client import IndexerClient  # type: ignore
from dydx_v4_client.network import TESTNET  # type: ignore


from locast.candle.candle import Candle

from locast.candle.exchange import Exchange
from locast.candle.exchange_candle_mapper import ExchangeCandleMapper
from locast.candle_fetcher.api_fetcher import APIFetcher
from locast.candle_fetcher.dydx.fetcher.datetime_format import datetime_to_dydx_iso_str


class DydxV4Fetcher(APIFetcher):
    def __init__(
        self, client: IndexerClient = IndexerClient(TESTNET.rest_indexer)
    ) -> None:
        self._client = client
        self._exchange = Exchange.DYDX_V4

    @property
    def exchange(self) -> Exchange:
        return self._exchange

    async def fetch(
        self,
        market: str,
        resolution: str,
        start_date: datetime,
        end_date: datetime,
    ) -> List[Candle]:
        response: Dict[
            str, Any
        ] = await self._client.markets.get_perpetual_market_candles(  # type: ignore
            market=market,
            resolution=resolution,
            from_iso=datetime_to_dydx_iso_str(start_date),
            to_iso=datetime_to_dydx_iso_str(end_date),
        )
        assert response["candles"]
        return ExchangeCandleMapper.to_candles(
            Exchange.DYDX_V4,
            response["candles"],
        )
