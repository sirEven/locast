from decimal import Decimal

from locast.candle.candle import Candle
from locast.candle_storage.sql.sqlite_candle import SqliteCandle


class ModelMapping:
    @staticmethod
    def to_candle(candle_entry: SqliteCandle) -> Candle:
        return Candle(
            id=candle_entry.id,
            exchange=candle_entry.exchange,
            market=candle_entry.market,
            resolution=candle_entry.resolution,
            started_at=candle_entry.started_at,
            open=Decimal(candle_entry.open),
            high=Decimal(candle_entry.high),
            low=Decimal(candle_entry.low),
            close=Decimal(candle_entry.close),
            base_token_volume=Decimal(candle_entry.base_token_volume),
            trades=candle_entry.trades,
            usd_volume=Decimal(candle_entry.usd_volume),
            starting_open_interest=Decimal(candle_entry.starting_open_interest),
        )

    @staticmethod
    def to_sqlite_candle(candle: Candle) -> SqliteCandle:
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
