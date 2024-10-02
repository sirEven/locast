from locast.candle.resolution import ResolutionDetail


class APIException(Exception):
    def __init__(
        self,
        market: str,
        resolution: ResolutionDetail,
        exception: Exception,
        message: str | None = None,
    ) -> None:
        if message is None:
            message = f"Error fetching market data for market '{market}' and resolution '{resolution.notation}: {exception}'."
        super().__init__(message)
