from locast.candle.resolution import (
    ResolutionDetail,
    ResolutionSeconds,
    ExchangeResolution,
)


class DydxResolution(ExchangeResolution):
    ONE_DAY = ResolutionDetail(ResolutionSeconds.ONE_DAY, "1DAY")
    FOUR_HOURS = ResolutionDetail(ResolutionSeconds.FOUR_HOURS, "4HOURS")
    ONE_HOUR = ResolutionDetail(ResolutionSeconds.ONE_HOUR, "1HOUR")
    THIRTY_MINUTES = ResolutionDetail(ResolutionSeconds.THIRTY_MINUTES, "30MINS")
    FIFTEEN_MINUTES = ResolutionDetail(ResolutionSeconds.FIFTEEN_MINUTES, "15MINS")
    FIVE_MINUTES = ResolutionDetail(ResolutionSeconds.FIVE_MINUTES, "5MINS")
    ONE_MINUTE = ResolutionDetail(ResolutionSeconds.ONE_MINUTE, "1MIN")
