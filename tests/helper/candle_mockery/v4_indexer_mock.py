from typing import Any, Dict, Optional


from dydx_v4_client.indexer.rest.indexer_client import IndexerClient, MarketsClient  # type: ignore
from dydx_v4_client.network import TESTNET  # type: ignore

from tests.helper.candle_mockery.mock_dydx_v4_candle_dicts import (
    mock_dydx_v4_candle_dict_batch,
)


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

        candle_dicts_batch = mock_dydx_v4_candle_dict_batch(
            resolution,
            market,
            from_iso,
            to_iso,
        )
        return {"candles": candle_dicts_batch}


class V4IndexerClientMock(IndexerClient):
    def __init__(self, host: str = TESTNET.rest_indexer) -> None:
        super().__init__(host=host)
        self._markets = V4MarketsClientMock()

    @property
    def markets(self) -> MarketsClient:
        return self._markets
