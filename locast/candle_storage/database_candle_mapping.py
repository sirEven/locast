from typing import Protocol, Any


from locast.candle.candle import Candle


class DatabaseCandleMapping(Protocol):
    def to_candle(self, database_candle: Any) -> Candle: ...

    def to_sqlite_candle(self, candle: Candle) -> Any: ...
