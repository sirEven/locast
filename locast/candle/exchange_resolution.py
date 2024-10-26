from dataclasses import dataclass
from abc import ABC
from enum import IntEnum


class Seconds(IntEnum):
    ONE_WEEK = 60 * 60 * 24 * 7
    ONE_DAY = 60 * 60 * 24
    FOUR_HOURS = 60 * 60 * 4
    ONE_HOUR = 60 * 60
    THIRTY_MINUTES = 60 * 30
    FIFTEEN_MINUTES = 60 * 15
    FIVE_MINUTES = 60 * 5
    ONE_MINUTE = 60


@dataclass
class ResolutionDetail:
    seconds: Seconds
    notation: str


# TODO: Consider this ABC generally - or think of functionality that should be moved/created here.
class ExchangeResolution(ABC):
    @classmethod
    def notation_to_resolution_detail(cls, notation: str) -> ResolutionDetail:
        seconds = cls._notation_to_seconds(notation)
        return ResolutionDetail(seconds, notation)

    @classmethod
    def _notation_to_seconds(cls, notation: str) -> Seconds:
        for attr in dir(cls):
            if (
                isinstance(getattr(cls, attr), ResolutionDetail)
                and getattr(cls, attr).notation == notation
            ):
                return getattr(cls, attr).seconds
        raise ValueError(f"Invalid notation: {notation}.")
