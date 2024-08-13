class StoreManager:
    def __init__(self) -> None:
        """Will take a CandleFetcher and a CandleStorage as input."""
        pass

    async def create_cluster(self) -> None:
        raise NotImplementedError

    async def update_cluster(self) -> None:
        raise NotImplementedError
