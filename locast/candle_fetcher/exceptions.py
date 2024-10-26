from locast.candle.exchange import Exchange
from locast.candle.exchange_resolution import ResolutionDetail


class APIException(Exception):
    def __init__(
        self,
        exchange: Exchange,
        market: str,
        resolution: ResolutionDetail,
        exception: Exception,
    ) -> None:
        msg = f"{exchange.name}: Error fetching market data for market '{market}' and resolution '{resolution.notation}: {exception}'."
        super().__init__(msg)
