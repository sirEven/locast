from typing import List

from locast.candle.resolution import ResolutionDetail, Seconds


resolutions: List[ResolutionDetail] = [
    ResolutionDetail(Seconds.ONE_MINUTE, "1MIN"),
    ResolutionDetail(Seconds.FIVE_MINUTES, "5MINS"),
    ResolutionDetail(Seconds.FIFTEEN_MINUTES, "15MINS"),
    ResolutionDetail(Seconds.THIRTY_MINUTES, "30MINS"),
    ResolutionDetail(Seconds.ONE_HOUR, "1HOUR"),
    ResolutionDetail(Seconds.FOUR_HOURS, "4HOURS"),
    ResolutionDetail(Seconds.ONE_DAY, "1DAY"),
]
