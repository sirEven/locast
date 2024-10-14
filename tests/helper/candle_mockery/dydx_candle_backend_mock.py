from typing import Any, Dict, List
from locast.candle.exchange import Exchange
from tests.helper.candle_mockery.mock_dydx_candle_dicts import (
    mock_dydx_candle_dict_batch,
)


class DydxCandleBackendMock:
    _instance = None

    def __new__(
        cls,
        missing_candles: bool | None = None,
        missing_candles_on_batch_end: bool | None = None,
        missing_candles_on_batch_start: bool | None = None,
    ):
        if cls._instance is None:
            cls._instance = super(DydxCandleBackendMock, cls).__new__(cls)
        return cls._instance

    def __init__(
        self,
        missing_candles: bool | None = None,
        missing_candles_on_batch_end: bool | None = None,
        missing_candles_on_batch_start: bool | None = None,
    ) -> None:
        if not hasattr(self, "_missing_candles"):
            self._missing_candles = missing_candles
            self._missing_candles_on_batch_end = missing_candles_on_batch_end
            self._missing_candles_on_batch_start = missing_candles_on_batch_start
            self._random_candles_deleted = False
            self._batch_end_deleted = False
            self._batch_start_deleted = False

    @property
    def missing_candles(self) -> bool | None:
        return self._missing_candles

    @missing_candles.setter
    def missing_candles(self, value: bool | None) -> None:
        self._missing_candles = value

    @property
    def missing_candles_on_batch_end(self) -> bool | None:
        return self._missing_candles_on_batch_end

    @missing_candles_on_batch_end.setter
    def missing_candles_on_batch_end(self, value: bool | None) -> None:
        self._missing_candles_on_batch_end = value

    @property
    def missing_candles_on_batch_start(self) -> bool | None:
        return self._missing_candles_on_batch_start

    @missing_candles_on_batch_start.setter
    def missing_candles_on_batch_start(self, value: bool | None) -> None:
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

        if self.missing_candles:
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
        if not self._random_candles_deleted:
            for n in [17, 23]:
                del batch[n]
            del batch[23]
            # TODO: Delete candles that fall on a batch boundary
            self._random_candles_deleted = True

    def _delete_on_batch_start(self, batch: List[Dict[str, Any]]):
        if not self._batch_start_deleted:
            del batch[0]
            self._batch_start_deleted = True

    def _delete_on_batch_end(self, batch: List[Dict[str, Any]]):
        if not self._batch_end_deleted:
            del batch[-1]
            self._batch_end_deleted = True
