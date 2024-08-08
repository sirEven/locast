import pytest

from locast.live_candle.dydx.dydx_live_candle import DydxV4LiveCandle
from tests.conftest import ETH_USD, ONE_MIN


@pytest.mark.asyncio
async def test_all_market_candles_are_live_after_start(
    dydx_v4_live_candle: DydxV4LiveCandle,
) -> None:
    # given
    live_candle = dydx_v4_live_candle

    # when
    await live_candle.start()

    # then
    assert live_candle.some_are_live()
    assert live_candle.all_are_live()


# FIXME: This test is (was? Can't reproduce) flaky...
@pytest.mark.asyncio
async def test_some_market_candles_are_live_after_unsubscribe(
    dydx_v4_live_candle: DydxV4LiveCandle,
) -> None:
    # given
    live_candle = dydx_v4_live_candle
    await live_candle.start()

    # when
    await live_candle.unsubscribe(ETH_USD, ONE_MIN.notation)

    # then
    assert live_candle.some_are_live()
    assert not live_candle.all_are_live()
