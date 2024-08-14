from datetime import datetime
from sqlmodel import Field, SQLModel  # type: ignore

from locast.candle.exchange import Exchange
from locast.candle.resolution import Seconds


# NOTE: For id to be NULL in db (which mackes no sense) you could set nullable=True.
class SqliteCandle(SQLModel, table=True):
    __tablename__ = "candle"  # type: ignore
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
