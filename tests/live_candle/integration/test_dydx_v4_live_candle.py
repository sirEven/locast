import pytest

from locast.candle.resolution import ResolutionDetail
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
    eth_usd: str,
    one_min: ResolutionDetail,
) -> None:
    # given
    live_candle = dydx_v4_live_candle
    await live_candle.start()

    # when
    await live_candle.unsubscribe(eth_usd, one_min.notation)

    # then
    assert live_candle.some_are_live()
    assert not live_candle.all_are_live()
