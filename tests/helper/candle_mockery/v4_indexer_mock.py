from typing import Any, Dict, Optional


from dydx_v4_client.indexer.rest.indexer_client import IndexerClient, MarketsClient  # type: ignore
from dydx_v4_client.network import TESTNET  # type: ignore

from locast.candle.exchange import Exchange
from tests.helper.candle_mockery.dydx_candle_backend_mock import DydxCandleBackendMock


# TODO: Implement horizon - meaning: After n returns, return []
class V4MarketsClientMock(MarketsClient):
    def __init__(self) -> None:
        pass

    async def get_perpetual_market_candles(
        self,
        market: str,
        resolution: str,
        from_iso: Optional[str] = None,
        to_iso: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        assert to_iso, "to_iso must be provided when mocking candles."
        assert from_iso, "from_iso must be provided when mocking candles."

        assert market.find("-") > 0, f"Invalid market: {market}."

        backend = DydxCandleBackendMock()
        return backend.mock_candles(
            Exchange.DYDX_V4,
            resolution,
            market,
            from_iso,
            to_iso,
            batch_size=1000,
        )


class V4IndexerClientMock(IndexerClient):
    def __init__(self, host: str = TESTNET.rest_indexer) -> None:
        super().__init__(host=host)
        self._markets = V4MarketsClientMock()

    @property
    def markets(self) -> MarketsClient:
        return self._markets
