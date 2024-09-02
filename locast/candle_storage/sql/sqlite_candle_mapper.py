from locast.candle_storage.database_candle_mapper import DatabaseCandleMapper
from locast.candle_storage.sql.sqlite_candle_mapping import SqliteCandleMapping


# TODO: I think we can ditch this one...
class SqliteCandleMapper(DatabaseCandleMapper):
    def __init__(self, mapping: SqliteCandleMapping) -> None:
        super().__init__(mapping)
