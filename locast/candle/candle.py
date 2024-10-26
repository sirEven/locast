from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from locast.candle.exchange_resolution import ResolutionDetail
from locast.candle.exchange import Exchange


class PricePoint(Enum):
    OPEN = "open"
    HIGH = "high"
    LOW = "low"
    CLOSE = "close"


@dataclass
class Candle:
    id: int | None
    exchange: Exchange
    market: str
    resolution: ResolutionDetail

    started_at: datetime

    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal

    base_token_volume: Decimal
    trades: int
    usd_volume: Decimal
    starting_open_interest: Decimal
