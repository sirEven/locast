from typing import Protocol


class LiveCandle(Protocol):
    def start(self) -> None: ...

    async def stop(self) -> None: ...
