from datetime import datetime
from decimal import Decimal
from sqlmodel import Field, SQLModel, create_engine  # type: ignore

from locast.candle.candle import Candle
from locast.candle.exchange import Exchange
from locast.candle.resolution import Seconds


# NOTE: For id to be NULL in db (which mackes no sense) you could set nullable=True.
class CandleEntry(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    exchange: Exchange
    market: str
    resolution: Seconds

    started_at: datetime

    open: str
    high: str
    low: str
    close: str

    base_token_volume: str
    trades: int
    usd_volume: str
    starting_open_interest: str


class ModelMapping:
    @staticmethod
    def to_candle(candle_entry: CandleEntry) -> Candle:
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
    def to_candle_entry(candle: Candle) -> CandleEntry:
        return CandleEntry(
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


sqlite_file_name = "candles.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
