from typing import List
import pytest
from sir_utilities.date_time import now_utc_iso

from locast.candle.candle import Candle
from locast.candle.candle_utility import CandleUtility as uc
from locast.candle.exchange import Exchange
from tests.helper.candle_mockery.mock_candle import mock_candle


def test_is_newest_valid_candles_returns_true() -> None:
    # given
    candle = mock_candle(Exchange.DYDX_V4)
    candle.started_at = now_utc_iso()
    newest_valid_date = uc.subtract_one_resolution(
        uc.norm_date(now_utc_iso(), candle.resolution),
        candle.resolution,
    )

    # when
    candle.started_at = newest_valid_date

    # then
    assert uc.is_newest_valid_candle(candle)


def test_is_newest_valid_candles_returns_false() -> None:
    # given
    candle = mock_candle(Exchange.DYDX_V4)
    newest_valid_date = uc.subtract_one_resolution(
        uc.norm_date(now_utc_iso(), candle.resolution),
        candle.resolution,
    )

    # when one resolution older than newest finished candle
    candle.started_at = uc.subtract_one_resolution(newest_valid_date, candle.resolution)

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
