from datetime import datetime, timedelta, timezone
from typing import List
from dataclasses import dataclass
from abc import ABC
from enum import IntEnum
from zoneinfo import ZoneInfo


class Seconds(IntEnum):
    ONE_WEEK = 60 * 60 * 24 * 7
    ONE_DAY = 60 * 60 * 24
    FOUR_HOURS = 60 * 60 * 4
    ONE_HOUR = 60 * 60
    THIRTY_MINUTES = 60 * 30
    FIFTEEN_MINUTES = 60 * 15
    FIVE_MINUTES = 60 * 5
    ONE_MINUTE = 60

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
class ResolutionDetail:
    seconds: Seconds
    notation: str


class ExchangeResolution(ABC):
    @classmethod
    def has_resolution(cls, res: Seconds) -> bool:
        resolutions = cls._resolution_list()
        for resolution in resolutions:
            if resolution.seconds == res:
                return True
        raise ValueError(
            f"Resolution {res.name} ({res} seconds) is not a {cls.__name__}"
        )

    @classmethod
    def notation_to_seconds(cls, notation: str) -> Seconds:
        resolutions = cls._resolution_list()

        for resolution in resolutions:
            if notation == resolution.notation:
                return resolution.seconds
        raise ValueError(f"Invalid notation: {notation}.")

    @classmethod
    def seconds_to_notation(cls, seconds: Seconds) -> str:
        resolutions = cls._resolution_list()

        for resolution in resolutions:
            if seconds == resolution.seconds:
                return resolution.notation
        raise ValueError(f"Invalid seconds: {seconds}")

    @classmethod
    def _resolution_list(cls) -> List[ResolutionDetail]:
        return [
            getattr(cls, attr)
            for attr in dir(cls)
            if isinstance(getattr(cls, attr), ResolutionDetail)
        ]
