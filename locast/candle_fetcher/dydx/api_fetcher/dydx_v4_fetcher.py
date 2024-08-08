from typing import Any, Dict, List

from dydx_v4_client.indexer.rest.indexer_client import IndexerClient  # type: ignore
from dydx_v4_client.network import TESTNET  # type: ignore


from locast.candle.candle import Candle

from locast.candle.exchange import Exchange
from locast.candle.exchange_candle_mapper import ExchangeCandleMapper


class DydxV4Fetcher:
    def __init__(
        self, client: IndexerClient = IndexerClient(TESTNET.rest_indexer)
    ) -> None:
        self._client = client

    async def fetch(
        self,
        market: str,
        resolution: str,
        start_date: str,
        end_date: str,
    ) -> List[Candle]:
        response: Dict[
            str, Any
        ] = await self._client.markets.get_perpetual_market_candles(  # type: ignore
            market=market,
            resolution=resolution,
            from_iso=start_date,
            to_iso=end_date,
        )
        assert response["candles"]
        return ExchangeCandleMapper.dicts_to_candles(
            Exchange.DYDX_V4,
            response["candles"],
        )
