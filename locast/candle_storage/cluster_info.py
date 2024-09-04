from dataclasses import dataclass

from locast.candle.candle import Candle


@dataclass
class ClusterInfo:
    head: Candle
    tail: Candle
    amount: int
    is_uptodate: bool
