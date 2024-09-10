from typing import Protocol


# TODO: Relocate this whole sub module either into the new bot once it is being started, or into its own module.
class LiveCandle(Protocol):
    async def start(self) -> None: ...

    async def stop(self) -> None: ...
