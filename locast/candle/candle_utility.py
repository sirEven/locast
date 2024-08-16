from enum import Enum
from logging import Logger
from typing import List, Set, Tuple, Type, TypeVar, Union
from zoneinfo import ZoneInfo
from datetime import datetime, timedelta, timezone
from locast.candle.candle import Candle
from locast.candle.exchange import Exchange
from locast.candle.resolution import Seconds

EnumType = TypeVar("EnumType", bound=Enum)


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
    def valid_up_to(cls, resolution: Seconds) -> datetime:
        # check the most recent date at which candles for this resolution are valid
        last_tick = cls.last_tick(resolution)
        return (last_tick - timedelta(seconds=resolution)).replace(
            tzinfo=ZoneInfo("UTC")
        )

    @classmethod
    def last_tick(cls, resolution_seconds: int) -> datetime:
        # calculate the last tick date of that resolution
        utc_now = datetime.now(timezone.utc)
        unix_epoch = datetime.fromtimestamp(0, timezone.utc)
        now_seconds = (utc_now - unix_epoch).total_seconds()

        remainder_sec = now_seconds % resolution_seconds
        last_tick_sec = now_seconds - remainder_sec
        return datetime.fromtimestamp(last_tick_sec, ZoneInfo("UTC"))

    @classmethod
    def norm_date(cls, date: datetime, res: Seconds) -> datetime:
        """
        Normalize a given datetime to the nearest lower multiple of a given resolution.
        In other words: Round down a date by a given resolution.
        Examples:
        12:37:12 rounded down by 1min resolution becomes 12:37
        12:37:12 rounded down by 5min resolution becomes 12:35
        12:37:12 rounded down by 15min resolution becomes 12:30

        Args:
            date (datetime): The datetime to be normalized.
            res (Seconds): The resolution to which the datetime should be normalized.

        Returns:
            datetime: The normalized datetime.
        """
        # Calculate the number of seconds since a reference datetime (e.g., epoch)
        seconds_since_reference = (
            date - datetime(1970, 1, 1, tzinfo=date.tzinfo)
        ).total_seconds()

        # Calculate the normalized seconds
        normalized_seconds = int(seconds_since_reference) - (
            int(seconds_since_reference) % res
        )

        # Create a new datetime with the normalized seconds
        return datetime(1970, 1, 1, tzinfo=date.tzinfo) + timedelta(
            seconds=normalized_seconds
        )

    @classmethod
    def normalized_now(cls, resolution: Seconds) -> datetime:
        # Generate the startedAt date for the newest finished candle (now - 1 res)
        return cls.norm_date(datetime.now(timezone.utc), resolution)

    @classmethod
    def subtract_one_resolution(cls, date: datetime, resolution: Seconds) -> datetime:
        return date - timedelta(seconds=resolution)

    @classmethod
    def add_one_resolution(cls, date: datetime, resolution: Seconds) -> datetime:
        return date + timedelta(seconds=resolution)

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
    def cluster_id_from_candle(cls, candle: Candle) -> str:
        exchange = candle.exchange
        market = candle.market
        resolution = candle.resolution

        return cls._concat_id(exchange, market, resolution)

    @classmethod
    def cluster_id_from_details(
        cls,
        exchange: Exchange,
        market: str,
        resolution: Seconds,
    ) -> str:
        return cls._concat_id(exchange, market, resolution)

    @classmethod
    def details_from_cluster_id(cls, cluster_id: str) -> Tuple[Exchange, str, Seconds]:
        details_str = cluster_id.split("_", maxsplit=2)
        exchange_str = details_str[0]
        market_str = details_str[1]
        res_str = details_str[2]

        exchange: Exchange | None = cls._find_enum_entry_by_value(
            exchange_str, Exchange
        )
        resolution: Seconds | None = cls._find_enum_entry_by_name(res_str, Seconds)
        assert exchange and resolution, f"Exchagne or resolution unkown ({__name__})."
        return (exchange, market_str, resolution)

    @classmethod
    def _concat_id(cls, exchange: Exchange, market: str, resolution: Seconds) -> str:
        return f"{exchange.value}_{market}_{resolution.name}"

    @classmethod
    def assert_chronologic_order(cls, candles: List[Candle]) -> None:
        # All date diffs == 1 res (no gaps, no duplicates, right order)
        assert candles
        res = candles[0].resolution
        for i, candle in enumerate(candles):
            if i > 0:
                msg = "Order violated from Candles"
                new = candles[i - 1].started_at
                old = candle.started_at
                assert candles[i - 1].started_at - candle.started_at == timedelta(
                    seconds=res
                ), f"{msg} {candle.id} ({old}) to {candles[i - 1].id} ({new})."

    @classmethod
    def amount_of_candles_in_range(
        cls,
        start_date: datetime,
        end_date: datetime,
        resolution: Seconds,
    ) -> int:
        assert start_date <= end_date, "start_date must be before end_date."

        range_seconds = (end_date - start_date).total_seconds()
        return int(range_seconds / resolution)

    @classmethod
    def remove_duplicates(
        cls,
        candles: List[Candle],
        logger: Logger,
    ) -> List[Candle]:
        # start = time.time()
        # logger.debug("Start removing duplicates")
        seen: Set[datetime] = set()
        unique_candles: List[Candle] = []
        double_count = 0

        for candle in candles:
            if candle.started_at not in seen:
                unique_candles.append(candle)
                seen.add(candle.started_at)
            else:
                double_count += 1

        # elapsed = round(time.time() - start, 2)
        # logger.debug(f"Finished removing {double_count} duplicates ({elapsed} sec)")
        return unique_candles

    @classmethod
    def _find_enum_entry_by_value(
        cls, value: str, enum: Type[EnumType]
    ) -> Union[EnumType, None]:
        enum_entry: Union[EnumType, None] = next(
            (enum_member for enum_member in enum if enum_member.value == value),
            None,
        )
        return enum_entry

    @classmethod
    def _find_enum_entry_by_name(
        cls, name: str, enum: Type[EnumType]
    ) -> Union[EnumType, None]:
        enum_entry: Union[EnumType, None] = next(
            (enum_member for enum_member in enum if enum_member.name == name), None
        )
        return enum_entry


# @classmethod
# def date_is_in(cls, candles: List[Candle], date: datetime) -> bool:
#     candle_started_at_set = {candle.started_at for candle in candles}
#     return date in candle_started_at_set
