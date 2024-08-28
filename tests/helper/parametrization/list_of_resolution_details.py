from typing import List

from locast.candle.dydx.dydx_resolution import DydxResolution
from locast.candle.resolution import ResolutionDetail


resolutions: List[ResolutionDetail] = [
    DydxResolution.ONE_MINUTE,
    DydxResolution.FIVE_MINUTES,
    DydxResolution.FIFTEEN_MINUTES,
    DydxResolution.THIRTY_MINUTES,
    DydxResolution.ONE_HOUR,
    # DydxResolution.FOUR_HOURS, NOTE: These will be too big for a while...
    # DydxResolution.ONE_DAY,
]
