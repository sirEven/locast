from typing import Any, Dict, Protocol, runtime_checkable

from locast.candle.exchange import Exchange


@runtime_checkable
class CandleBackendMock(Protocol):
    @property
    def missing_random_candles(self) -> int: ...

    @missing_random_candles.setter
    def missing_random_candles(self, value: int) -> None: ...

    @property
    def missing_candles_on_batch_newest_edge(self) -> int: ...

    @missing_candles_on_batch_newest_edge.setter
    def missing_candles_on_batch_newest_edge(self, value: int) -> None: ...

    def mock_candles(
        self,
        exchange: Exchange,
        resolution: str,
        market: str,
        from_iso: str,
        to_iso: str,
        batch_size: int,
    ) -> Dict[str, Any]: ...

    @classmethod
    def reset_instance(cls) -> None: ...
