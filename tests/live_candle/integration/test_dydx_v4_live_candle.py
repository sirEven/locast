import pytest

from locast.candle.dydx.dydx_resolution import DydxResolution
from locast.live_candle.dydx.dydx_live_candle import DydxV4LiveCandle


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


@pytest.mark.asyncio
async def test_some_market_candles_are_live_after_unsubscribe(
    dydx_v4_live_candle: DydxV4LiveCandle,
) -> None:
    # given
    eth_usd = "ETH-USD"
    one_min = DydxResolution.ONE_MINUTE.notation
    live_candle = dydx_v4_live_candle
    await live_candle.start()

    # when
    await live_candle.unsubscribe(eth_usd, one_min)

    # then
    assert live_candle.some_are_live()
    assert not live_candle.all_are_live()
