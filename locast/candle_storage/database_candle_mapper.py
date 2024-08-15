from typing import Any
from locast.candle.candle import Candle
from locast.candle_storage.database_type import DatabaseType
from locast.candle_storage.sql.sqlite_candle_mapping import SqliteCandleMapping


class DatabaseCandleMapper:
    """
    A class that maps candle representations from different database technologies to Candle objects.
    """

    mappings = {DatabaseType.SQLITE: SqliteCandleMapping()}

    @staticmethod
    def to_candle(database: DatabaseType, database_candle: Any) -> Candle:
        mapping = DatabaseCandleMapper._select_db_type(database)
        return mapping.to_candle(database_candle)

    @staticmethod
    def to_database_candle(database: DatabaseType, candle: Candle) -> Any:
        mapping = DatabaseCandleMapper._select_db_type(database)
        return mapping.to_sqlite_candle(candle)

    @staticmethod
    def _select_db_type(database: DatabaseType):
        if not (mapping := DatabaseCandleMapper.mappings.get(database)):
            raise ValueError(
                f"Candle can't be mapped for unknown database type: {database}."
            )

        return mapping
