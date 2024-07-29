from datetime import datetime, timedelta, timezone
from typing import List
from dataclasses import dataclass
from abc import ABC
from enum import IntEnum
from zoneinfo import ZoneInfo


class Resolution(IntEnum):
    r_1WEEK = 60 * 60 * 24 * 7
    r_1DAY = 60 * 60 * 24
    r_4HOURS = 60 * 60 * 4
    r_1HOUR = 60 * 60
    r_30MINS = 60 * 30
    r_15MINS = 60 * 15
    r_5MINS = 60 * 5
    r_1MIN = 60

    def next_tick(self) -> datetime:
        res_sec = self.value
        utc_now = datetime.now(timezone.utc)
        unix_epoch = datetime.fromtimestamp(0, timezone.utc)
        now_seconds = (utc_now - unix_epoch).total_seconds()

        remainder_sec = now_seconds % res_sec
        last_tick_sec = now_seconds - remainder_sec
        last_tick = datetime.fromtimestamp(last_tick_sec, ZoneInfo("UTC"))
        return last_tick + timedelta(seconds=res_sec)


@dataclass
class ResolutionTrait:
    seconds: Resolution
    notation: str


class ExchangeResolution(ABC):
    @classmethod
    def has_resolution(cls, res: Resolution) -> bool:
        resolutions = cls._resolution_list()
        for resolution in resolutions:
            if resolution.seconds == res:
                return True
        raise ValueError(
            f"Resolution {res.name} ({res} seconds) is not a {cls.__name__}"
        )

    @classmethod
    def notation_to_seconds(cls, notation: str) -> Resolution:
        resolutions = cls._resolution_list()

        for resolution in resolutions:
            if notation == resolution.notation:
                return resolution.seconds
        raise ValueError(f"Invalid notation: {notation}.")

    @classmethod
    def seconds_to_notation(cls, seconds: Resolution) -> str:
        resolutions = cls._resolution_list()

        for resolution in resolutions:
            if seconds == resolution.seconds:
                return resolution.notation
        raise ValueError(f"Invalid seconds: {seconds}")

    @classmethod
    def _resolution_list(cls) -> List[ResolutionTrait]:
        return [
            getattr(cls, attr)
            for attr in dir(cls)
            if isinstance(getattr(cls, attr), ResolutionTrait)
        ]
