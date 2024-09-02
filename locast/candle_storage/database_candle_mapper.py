from typing import Any

from locast.candle.candle import Candle
from locast.candle_storage.database_candle_mapping import DatabaseCandleMapping


class DatabaseCandleMapper:
    """
    Maps candle representations from different database technologies to Candle objects and vice versa.
    """

    def __init__(self, mapping: DatabaseCandleMapping) -> None:
        self._mapping = mapping

    def to_candle(self, database_candle: Any) -> Candle:
        return self._mapping.to_candle(database_candle)

    def to_database_candle(self, candle: Candle) -> Any:
        return self._mapping.to_database_candle(candle)
