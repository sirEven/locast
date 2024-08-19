from typing import Any

from sqlalchemy import Engine
from locast.candle.candle import Candle
from locast.candle_storage.database_candle_mapping import DatabaseCandleMapping
from locast.candle_storage.database_type import DatabaseType
from locast.candle_storage.sql.sqlite_candle_mapping import SqliteCandleMapping


class DatabaseCandleMapper:
    """
    A class that maps candle representations from different database technologies to Candle objects and vice versa.
    """

    def __init__(self, sqlite_engine: Engine | None) -> None:
        self._mappings: dict[DatabaseType, DatabaseCandleMapping] = {}
        if sqlite_engine:
            self._mappings[DatabaseType.SQLITE] = SqliteCandleMapping(sqlite_engine)

    def to_candle(self, database: DatabaseType, database_candle: Any) -> Candle:
        mapping = self._select_mapping(database)
        return mapping.to_candle(database_candle)

    def to_database_candle(self, database: DatabaseType, candle: Candle) -> Any:
        mapping = self._select_mapping(database)
        return mapping.to_database_candle(candle)

    def _select_mapping(self, database: DatabaseType) -> DatabaseCandleMapping:
        if not (mapping := self._mappings.get(database)):
            raise ValueError(
                f"Candle can't be mapped for unknown database type: {database}."
            )

        return mapping
