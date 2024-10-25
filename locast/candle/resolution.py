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


# TODO: Consider this ABC at all - or think of functionality that should be moved/created here.
class ExchangeResolution(ABC):
    @classmethod
    def notation_to_resolution_detail(cls, notation: str) -> ResolutionDetail:
        seconds = cls.notation_to_seconds(notation)
        return ResolutionDetail(seconds, notation)

    @classmethod
    def notation_to_seconds(cls, notation: str) -> Seconds:
        for attr in dir(cls):
            if (
                isinstance(getattr(cls, attr), ResolutionDetail)
                and getattr(cls, attr).notation == notation
            ):
                return getattr(cls, attr).seconds
        raise ValueError(f"Invalid notation: {notation}.")

    # @classmethod
    # def notation_to_seconds(cls, notation: str) -> Seconds:
    #     resolutions = cls._resolution_list()

    #     for resolution in resolutions:
    #         if notation == resolution.notation:
    #             return resolution.seconds
    #     raise ValueError(f"Invalid notation: {notation}.")

    # @classmethod
    # def seconds_to_notation(cls, seconds: Seconds) -> str:
    #     resolutions = cls._resolution_list()

    #     for resolution in resolutions:
    #         if seconds == resolution.seconds:
    #             return resolution.notation
    #     raise ValueError(f"Invalid seconds: {seconds}")

    # @classmethod
    # def _resolution_list(cls) -> List[ResolutionDetail]:
    #     return [
    #         getattr(cls, attr)
    #         for attr in dir(cls)
    #         if isinstance(getattr(cls, attr), ResolutionDetail)
    #     ]
