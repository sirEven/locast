from datetime import datetime, timedelta, timezone
from typing import List
import pytest
from sir_utilities.date_time import now_utc_iso

from locast.candle.candle import Candle
from locast.candle.candle_utility import CandleUtility as uc
from locast.candle.exchange import Exchange
from locast.candle.resolution import ResolutionDetail
from tests.helper.candle_mockery.mock_candle import mock_candle

from tests.helper.parametrization.list_of_resolution_details import resolutions


def test_is_newest_valid_candles_returns_true() -> None:
    # given
    candle = mock_candle(Exchange.DYDX_V4)
    candle.started_at = now_utc_iso()
    newest_valid_date = uc.subtract_n_resolutions(
        uc.norm_date(now_utc_iso(), candle.resolution),
        candle.resolution,
        1,
    )

    # when
    candle.started_at = newest_valid_date

    # then
    assert uc.is_newest_valid_candle(candle)


def test_is_newest_valid_candles_returns_false() -> None:
    # given
    candle = mock_candle(Exchange.DYDX_V4)
    newest_valid_date = uc.subtract_n_resolutions(
        uc.norm_date(now_utc_iso(), candle.resolution),
        candle.resolution,
        1,
    )

    # when one resolution older than newest finished candle
    candle.started_at = uc.subtract_n_resolutions(
        newest_valid_date,
        candle.resolution,
        1,
    )

    # then
    assert uc.is_newest_valid_candle(candle) is False


def test_assert_chronological_order_returns_true(
    dydx_v4_eth_one_min_mock_candles: List[Candle],
) -> None:
    # given
    candles = dydx_v4_eth_one_min_mock_candles

    # when & then
    uc.assert_chronologic_order(candles)


def test_assert_chronological_order_returns_false(
    dydx_v4_eth_one_min_mock_candles: List[Candle],
) -> None:
    # given
    candles = dydx_v4_eth_one_min_mock_candles
    faulty_candles = [candles[0], candles[1], candles[3], candles[4]]

    # when & then
    with pytest.raises(AssertionError):
        uc.assert_chronologic_order(faulty_candles)


def test_assert_candle_unity_returns_true(
    dydx_v4_eth_one_min_mock_candles: List[Candle],
) -> None:
    # given
    candles = dydx_v4_eth_one_min_mock_candles

    # when & then
    uc.assert_candle_unity(candles)


def test_assert_candle_unity_returns_false(
    dydx_v4_eth_one_min_mock_candles: List[Candle],
) -> None:
    # given
    candles = dydx_v4_eth_one_min_mock_candles
    candles[5].market = "BTC-USD"

    # when & then
    with pytest.raises(AssertionError):
        uc.assert_candle_unity(candles)


# Here we test behavior (returning None) when 0 or 1 candles are passed
@pytest.mark.parametrize("candles", [[], [mock_candle(Exchange.DYDX_V4)]])
def test_assert_candle_unity_does_not_raise(candles: List[Candle]) -> None:
    # given
    too_few_candles = candles
    # when & then
    uc.assert_candle_unity(too_few_candles)


@pytest.mark.parametrize("resolution", resolutions)
def test_next_tick_returns_correctly(resolution: ResolutionDetail) -> None:
    # given
    res = resolution

    # when
    next_tick = uc.next_tick(res)

    # then
    expected_next_tick = alternate_next_tick(res)
    assert next_tick == expected_next_tick


def alternate_next_tick(resolution: ResolutionDetail) -> datetime:
    utc_now = datetime.now(timezone.utc)
    unix_epoch = datetime.fromtimestamp(0, timezone.utc)
    now_seconds = (utc_now - unix_epoch).total_seconds()

    remainder_sec = now_seconds % resolution.seconds
    last_tick_sec = now_seconds - remainder_sec
    last_tick = datetime.fromtimestamp(last_tick_sec, timezone.utc)
    return last_tick + timedelta(seconds=resolution.seconds)
