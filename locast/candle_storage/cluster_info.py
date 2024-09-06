from dataclasses import dataclass

from locast.candle.candle import Candle


@dataclass
class ClusterInfo:
    head: Candle | None
    tail: Candle | None
    amount: int
    is_uptodate: bool
