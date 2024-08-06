from typing import Protocol


class LiveCandle(Protocol):
    async def start(self) -> None: ...

    async def stop(self) -> None: ...
