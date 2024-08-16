from decimal import Decimal

from locast.candle.candle import Candle
from locast.candle_storage.database_candle_mapping import DatabaseCandleMapping
from locast.candle_storage.sql.sqlite_candle import SqliteCandle


class SqliteCandleMapping(DatabaseCandleMapping):
    def to_candle(self, database_candle: SqliteCandle) -> Candle:
        return Candle(
            id=database_candle.id,
            exchange=database_candle.exchange,
            market=database_candle.market,
            resolution=database_candle.resolution,
            started_at=database_candle.started_at,
            open=Decimal(database_candle.open),
            high=Decimal(database_candle.high),
            low=Decimal(database_candle.low),
            close=Decimal(database_candle.close),
            base_token_volume=Decimal(database_candle.base_token_volume),
            trades=database_candle.trades,
            usd_volume=Decimal(database_candle.usd_volume),
            starting_open_interest=Decimal(database_candle.starting_open_interest),
        )

    def to_database_candle(self, candle: Candle) -> SqliteCandle:
        return SqliteCandle(
            id=candle.id,
            exchange=candle.exchange,
            market=candle.market,
            resolution=candle.resolution,
            started_at=candle.started_at,
            open=str(candle.open),
            high=str(candle.high),
            low=str(candle.low),
            close=str(candle.close),
            base_token_volume=str(candle.base_token_volume),
            trades=candle.trades,
            usd_volume=str(candle.usd_volume),
            starting_open_interest=str(candle.starting_open_interest),
        )
