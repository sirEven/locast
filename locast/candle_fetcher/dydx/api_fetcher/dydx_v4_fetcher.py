from datetime import datetime
from typing import Any, Dict, List

from dydx_v4_client.indexer.rest.indexer_client import IndexerClient  # type: ignore
from dydx_v4_client.network import TESTNET  # type: ignore


from locast.candle.candle import Candle

from locast.candle.dydx.dydx_candle_mapping import DydxV4CandleMapping
from locast.candle.exchange import Exchange
from locast.candle.exchange_candle_mapper import ExchangeCandleMapper
from locast.candle.exchange_resolution import ResolutionDetail
from locast.candle_fetcher.dydx.api_fetcher.datetime_format import (
    datetime_to_dydx_iso_str,
)
from locast.candle_fetcher.dydx.api_fetcher.dydx_fetcher import DydxFetcher
from locast.candle_fetcher.exceptions import APIException


class DydxV4Fetcher(DydxFetcher):
    def __init__(
        self,
        client: IndexerClient = IndexerClient(TESTNET.rest_indexer),
    ) -> None:
        self._exchange = Exchange.DYDX_V4
        self._client = client
        self._mapper = ExchangeCandleMapper(DydxV4CandleMapping())

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
        try:
            response: Dict[
                str,
                Any,
            ] = await self._client.markets.get_perpetual_market_candles(  # type: ignore
                market=market,
                resolution=resolution.notation,
                from_iso=datetime_to_dydx_iso_str(start_date),
                to_iso=datetime_to_dydx_iso_str(end_date),
            )

        except Exception as e:
            raise APIException(self._exchange, market, resolution, e) from e

        return self._mapper.to_candles(response["candles"])
