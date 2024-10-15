import random
from typing import Any, Dict, List
from locast.candle.exchange import Exchange
from tests.helper.candle_mockery.mock_dydx_candle_dicts import (
    mock_dydx_candle_dict_batch,
)


class DydxCandleBackendMock:
    _instance = None

    def __new__(
        cls,
        missing_random_candles: int = 0,
        missing_candles_on_batch_end: int = 0,
        missing_candles_on_batch_start: int = 0,
    ):
        if cls._instance is None:
            cls._instance = super(DydxCandleBackendMock, cls).__new__(cls)
        return cls._instance

    def __init__(
        self,
        missing_random_candles: int = 0,
        missing_candles_on_batch_end: int = 0,
        missing_candles_on_batch_start: int = 0,
    ) -> None:
        properties = {
            "_missing_random_candles": missing_random_candles,
            "_missing_candles_on_batch_end": missing_candles_on_batch_end,
            "_missing_candles_on_batch_start": missing_candles_on_batch_start,
        }
        for prop, value in properties.items():
            if not hasattr(self, prop):
                setattr(self, prop, value)
                # Initialize corresponding deleted flag
                deleted_prop = f"{prop}_deleted"
                setattr(self, deleted_prop, False)

    @property
    def missing_random_candles(self) -> int:
        return self._missing_random_candles

    @missing_random_candles.setter
    def missing_random_candles(self, value: int) -> None:
        self._missing_random_candles = value

    @property
    def missing_candles_on_batch_end(self) -> int:
        return self._missing_candles_on_batch_end

    @missing_candles_on_batch_end.setter
    def missing_candles_on_batch_end(self, value: int) -> None:
        self._missing_candles_on_batch_end = value

    @property
    def missing_candles_on_batch_start(self) -> int:
        return self._missing_candles_on_batch_start

    @missing_candles_on_batch_start.setter
    def missing_candles_on_batch_start(self, value: int) -> None:
        self._missing_candles_on_batch_start = value

    def mock_candles(
        self,
        exchange: Exchange,
        resolution: str,
        market: str,
        from_iso: str,
        to_iso: str,
        batch_size: int,
    ) -> Dict[str, Any]:
        candle_dicts_batch = mock_dydx_candle_dict_batch(
            exchange,
            resolution,
            market,
            from_iso,
            to_iso,
            batch_size,
        )

        if self._missing_random_candles:
            self._delete_random_candles(candle_dicts_batch)

        if self._missing_candles_on_batch_end:
            self._delete_on_batch_end(candle_dicts_batch)

        if self._missing_candles_on_batch_start:
            self._delete_on_batch_start(candle_dicts_batch)

        return {"candles": candle_dicts_batch}

    @classmethod
    def reset_instance(cls) -> None:
        cls._instance = None

    def _delete_random_candles(self, batch: List[Dict[str, Any]]) -> None:
        if not self._missing_random_candles_deleted:
            for _ in range(self._missing_random_candles):
                del batch[random.randint(10, 20)]
            self._missing_random_candles_deleted = True

    def _delete_on_batch_start(self, batch: List[Dict[str, Any]]):
        if not self._missing_candles_on_batch_start_deleted:
            del batch[0]
            self._missing_candles_on_batch_start_deleted = True

    def _delete_on_batch_end(self, batch: List[Dict[str, Any]]):
        if not self._missing_candles_on_batch_end_deleted:
            del batch[-1]
            self._missing_candles_on_batch_end_deleted = True
