from datetime import datetime
from sqlalchemy import Index, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel  # type: ignore

from locast.candle.exchange import Exchange
from locast.candle.resolution import Seconds


class SqliteExchange(SQLModel, table=True):
    __tablename__ = "exchange"  # type: ignore
    id: int | None = Field(default=None, primary_key=True)
    exchange: Exchange = Field(nullable=False, unique=True)


class SqliteResolution(SQLModel, table=True):
    __tablename__ = "resolution"  # type: ignore
    id: int | None = Field(default=None, primary_key=True)
    seconds: Seconds = Field(nullable=False, unique=True)
    notation: str = Field(nullable=False, unique=True)


class SqliteMarket(SQLModel, table=True):
    __tablename__ = "market"  # type: ignore
    id: int | None = Field(default=None, primary_key=True)
    market: str = Field(nullable=False, unique=True)


# NOTE: For id to be NULL in db (which makes no sense) you could set nullable=True.
class SqliteCandle(SQLModel, table=True):
    __tablename__ = "candle"  # type: ignore
    id: int | None = Field(default=None, primary_key=True)
    # TODO: Check why we have | None here when in fact they are not nullable.
    exchange_id: int | None = Field(
        default=None,
        foreign_key=("exchange.id"),
        nullable=False,
        index=True,
    )
    market_id: int | None = Field(
        default=None,
        foreign_key=("market.id"),
        nullable=False,
        index=True,
    )
    resolution_id: int | None = Field(
        default=None,
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

    # Relationships
    exchange: SqliteExchange = Relationship()
    market: SqliteMarket = Relationship()
    resolution: SqliteResolution = Relationship()

    __table_args__ = (
        Index(
            "compound_index_exchange_market_resolution",
            "exchange_id",
            "market_id",
            "resolution_id",
        ),
        UniqueConstraint(
            "exchange_id",
            "market_id",
            "resolution_id",
            "started_at",
            name="unique_candle_constraint",
        ),
    )
