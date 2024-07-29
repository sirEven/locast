from locast.candle.resolution import (
    ResolutionTrait,
    Resolution,
    ExchangeResolution,
)


class DydxResolution(ExchangeResolution):
    r_1DAY = ResolutionTrait(Resolution.r_1DAY, "1DAY")
    r_4HOURS = ResolutionTrait(Resolution.r_4HOURS, "4HOURS")
    r_1HOUR = ResolutionTrait(Resolution.r_1HOUR, "1HOUR")
    r_30MINS = ResolutionTrait(Resolution.r_30MINS, "30MINS")
    r_15MINS = ResolutionTrait(Resolution.r_15MINS, "15MINS")
    r_5MINS = ResolutionTrait(Resolution.r_5MINS, "5MINS")
    r_1MIN = ResolutionTrait(Resolution.r_1MIN, "1MIN")
