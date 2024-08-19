from datetime import datetime
from sqlalchemy import Index
from sqlmodel import Field, SQLModel  # type: ignore


from locast.candle.exchange import Exchange
from locast.candle.resolution import Seconds


# NOTE: For id to be NULL in db (which makes no sense) you could set nullable=True.
class SqliteCandle(SQLModel, table=True):
    __tablename__ = "candle"  # type: ignore
    id: int | None = Field(default=None, primary_key=True)

    exchange_id: int = Field(
        foreign_key=("exchange.id"),
        nullable=False,
        index=True,
    )
    market_id: int = Field(
        foreign_key=("market.id"),
        nullable=False,
        index=True,
    )
    resolution_id: int = Field(
        foreign_key=("resolution.id"),
        nullable=False,
        index=True,
    )

    started_at: datetime

    open: str
    high: str
    low: str
    close: str

    base_token_volume: str
    trades: int
    usd_volume: str
    starting_open_interest: str

    __table_args__ = (
        Index(
            "compound_index_exchange_market_resolution",
            "exchange_id",
            "market_id",
            "resolution_id",
        ),
    )


class SqliteExchange(SQLModel, table=True):
    __tablename__ = "exchange"  # type: ignore
    id: int | None = Field(default=None, primary_key=True)
    exchange: Exchange = Field(nullable=False, unique=True)


class SqliteResolution(SQLModel, table=True):
    __tablename__ = "resolution"  # type: ignore
    id: int | None = Field(default=None, primary_key=True)
    resolution: Seconds = Field(nullable=False, unique=True)


class SqliteMarket(SQLModel, table=True):
    __tablename__ = "market"  # type: ignore
    id: int | None = Field(default=None, primary_key=True)
    market: str = Field(nullable=False, unique=True)
