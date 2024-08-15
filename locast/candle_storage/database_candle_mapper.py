from locast.candle_storage.database_type import Database
from locast.candle_storage.sql.sqlite_candle_mapping import SqliteCandleMapping


class DatabaseCandleMapper:
    """
    A class that maps candle representations from different database technologies to Candle objects.
    """

    mappings = {Database.SQLITE: SqliteCandleMapping()}
