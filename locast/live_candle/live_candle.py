from typing import Protocol


class LiveCandle(Protocol):
    def start(self) -> None: ...

    def stop(self) -> None: ...
