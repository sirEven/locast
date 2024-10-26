from locast.candle.exchange_resolution import (
    ResolutionDetail,
    Seconds,
    ExchangeResolution,
)


class DydxResolution(ExchangeResolution):
    ONE_DAY = ResolutionDetail(Seconds.ONE_DAY, "1DAY")
    FOUR_HOURS = ResolutionDetail(Seconds.FOUR_HOURS, "4HOURS")
    ONE_HOUR = ResolutionDetail(Seconds.ONE_HOUR, "1HOUR")
    THIRTY_MINUTES = ResolutionDetail(Seconds.THIRTY_MINUTES, "30MINS")
    FIFTEEN_MINUTES = ResolutionDetail(Seconds.FIFTEEN_MINUTES, "15MINS")
    FIVE_MINUTES = ResolutionDetail(Seconds.FIVE_MINUTES, "5MINS")
    ONE_MINUTE = ResolutionDetail(Seconds.ONE_MINUTE, "1MIN")
