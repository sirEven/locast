from dataclasses import dataclass

from locast.candle.candle import Candle


@dataclass
class ClusterInfo:
    newest_candle: Candle | None
    oldest_candle: Candle | None
    size: int
    is_uptodate: bool
