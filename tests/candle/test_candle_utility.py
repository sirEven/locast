from sir_utilities.date_time import now_utc_iso

from locast.candle.candle import Candle
from locast.candle.candle_utility import CandleUtility as uc


# TODO: test all functions of CandleUtility
def test_is_newest_valid_candles_returns_true(dummy_candle: Candle) -> None:
    # given
    candle = dummy_candle
    newest_valid_date = uc.subtract_one_resolution(
        uc.norm_date(now_utc_iso(), candle.resolution),
        candle.resolution,
    )

    # when
    candle.started_at = newest_valid_date

    # then
    assert uc.is_newest_valid_candle(candle)


def test_is_newest_valid_candles_returns_false(dummy_candle: Candle) -> None:
    # given
    candle = dummy_candle
    newest_valid_date = uc.subtract_one_resolution(
        uc.norm_date(now_utc_iso(), candle.resolution),
        candle.resolution,
    )

    # when one resolution older than newest finished candle
    candle.started_at = uc.subtract_one_resolution(newest_valid_date, candle.resolution)

    # then
    assert uc.is_newest_valid_candle(candle) is False
