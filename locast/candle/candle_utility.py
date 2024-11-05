from enum import Enum
from typing import List, TypeVar
from zoneinfo import ZoneInfo
from datetime import datetime, timedelta, timezone
from locast.candle.candle import Candle
from locast.candle.exchange_resolution import ResolutionDetail

EnumType = TypeVar("EnumType", bound=Enum)

# TODO: Check what functions are not needed anymore.


class CandleUtility:
    @classmethod
    def is_newest_valid_candle(
        cls,
        candle: Candle,
    ) -> bool:
        # valid_up_to is the date a newest candle should have as started_at in order
        # to be valid - if candle.started_at differs from it, the candle is either
        # unfinished (its date is newer than valid_up_to) or not the newest, (its date
        # lacks behind) meaning we have a gap to fill.
        valid_up_to = cls.valid_up_to(candle.resolution)
        started_at = candle.started_at.replace(tzinfo=ZoneInfo("UTC"))

        return started_at == valid_up_to

    @classmethod
    def valid_up_to(cls, resolution: ResolutionDetail) -> datetime:
        # check the most recent date at which candles for this resolution are valid
        last_tick = cls.norm_date(datetime.now(timezone.utc), resolution)
        return (last_tick - timedelta(seconds=resolution.seconds)).replace(
            tzinfo=ZoneInfo("UTC")
        )

    # @classmethod
    # def last_tick(cls, resolution: ResolutionDetail) -> datetime:
    #     # calculate the last tick date of that resolution
    #     utc_now = datetime.now(timezone.utc)
    #     unix_epoch = datetime.fromtimestamp(0, timezone.utc)
    #     now_seconds = (utc_now - unix_epoch).total_seconds()

    #     remainder_sec = now_seconds % resolution.seconds
    #     last_tick_sec = now_seconds - remainder_sec
    #     return datetime.fromtimestamp(last_tick_sec, ZoneInfo("UTC"))

    @classmethod
    def next_tick(cls, resolution: ResolutionDetail) -> datetime:
        utc_now = cls.norm_date(datetime.now(timezone.utc), resolution)
        return utc_now + timedelta(
            seconds=resolution.seconds - (utc_now.second % resolution.seconds)
        )

    @classmethod
    def norm_date(cls, date: datetime, resolution: ResolutionDetail) -> datetime:
        """
        Normalize a given datetime to the nearest lower multiple of a given resolution.
        In other words: Round down a date by a given resolution.
        Examples:
        12:37:12 rounded down by 1min resolution becomes 12:37
        12:37:12 rounded down by 5min resolution becomes 12:35
        12:37:12 rounded down by 15min resolution becomes 12:30


        Args:
            date (datetime): The datetime to be normalized.
            resolution (ResolutionDetail): The resolution to which the datetime should be normalized.


        Returns:
            datetime: The normalized datetime.
        """
        # Calculate the number of seconds since the epoch
        seconds_since_epoch = (
            date - datetime.fromtimestamp(0, tz=date.tzinfo)
        ).total_seconds()

        # Calculate the normalized seconds
        normalized_seconds = seconds_since_epoch - (
            seconds_since_epoch % resolution.seconds
        )

        # Create a new datetime with the normalized seconds
        return datetime.fromtimestamp(0, tz=date.tzinfo) + timedelta(
            seconds=normalized_seconds
        )

    @classmethod
    def normalized_now(cls, resolution: ResolutionDetail) -> datetime:
        # Generate the startedAt date for the newest finished candle (now - 1 res)
        return cls.norm_date(datetime.now(timezone.utc), resolution)

    @classmethod
    def subtract_n_resolutions(
        cls,
        date: datetime,
        resolution: ResolutionDetail,
        n: int,
    ) -> datetime:
        return date - timedelta(seconds=resolution.seconds * n)

    @classmethod
    def add_one_resolution(
        cls,
        date: datetime,
        resolution: ResolutionDetail,
    ) -> datetime:
        return date + timedelta(seconds=resolution.seconds)

    @classmethod
    def assert_candle_unity(cls, candles: List[Candle]) -> None:
        if len(candles) <= 1:
            return
        market = candles[0].market
        resolution = candles[0].resolution
        exchange = candles[0].exchange

        fail_value = None
        try:
            fail_value = next(
                (index, candle)
                for index, candle in enumerate(candles)
                if candle.market != market
                or candle.exchange != exchange
                or candle.resolution != resolution
            )
        except StopIteration:
            return
        index, candle = fail_value
        msg = "Candles need to be identical in exchange, market & resolution"
        mismatch = f"(candle #{index} is a mismatch: {candle})."
        raise AssertionError(f"{msg} {mismatch}")

    @classmethod
    def detect_missing_dates(
        cls,
        candle_dates: List[datetime],
        resolution: ResolutionDetail,
    ) -> List[datetime]:
        missing: List[datetime] = []

        if len(candle_dates) <= 1:
            return missing

        diff_ok = resolution.seconds
        for i, candle_date in enumerate(candle_dates):
            if i > 0:
                new = candle_dates[i - 1]
                old = candle_date
                if new - old != diff_ok:
                    missing_dates = cls.missing_dates_between(
                        old,
                        new,
                        resolution,
                    )
                    missing.extend(missing_dates)
        return missing

    @classmethod
    def amount_of_candles_in_range(
        cls,
        start_date: datetime,
        end_date: datetime,
        resolution: ResolutionDetail,
    ) -> int:
        assert start_date <= end_date, "start_date must be before end_date."

        range_seconds = (end_date - start_date).total_seconds()
        return int(range_seconds / resolution.seconds)

    @classmethod
    def amount_missing(
        cls,
        start_date: datetime,
        end_date: datetime,
        resolution: ResolutionDetail,
    ) -> int:
        return cls.amount_of_candles_in_range(start_date, end_date, resolution) - 1

    @classmethod
    def missing_dates_between(
        cls,
        start_date: datetime,
        end_date: datetime,
        resolution: ResolutionDetail,
    ) -> List[datetime]:
        missing_dates: List[datetime] = []
        current_date = start_date + timedelta(seconds=resolution.seconds)
        while current_date < end_date:
            missing_dates.append(current_date)
            current_date += timedelta(seconds=resolution.seconds)
        return missing_dates

    @classmethod
    def midpoint(cls, start: datetime, end: datetime) -> datetime:
        # Calculate the midpoint between two datetime objects.
        return start + (end - start) / 2
