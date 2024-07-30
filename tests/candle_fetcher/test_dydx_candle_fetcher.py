import pytest
from locast.candle.dydx.dydx_resolution import DydxResolution
from locast.candle.exchange import Exchange
from locast.candle_fetcher.dydx.dydx_candle_fetcher import DydxCandleFetcher


@pytest.mark.asyncio
async def test_v4_fetch_600_historic_candles() -> None:
    # given
    fetcher = DydxCandleFetcher()
    start = "2024-04-01T00:00:00.000Z"
    end = "2024-04-01T10:00:00.000Z"

    # when
    candles = await fetcher.fetch_historic_candles(
        Exchange.DYDX_V4,
        "ETH-USD",
        DydxResolution.ONE_MINUTE.notation,
        start,
        end,
    )

    # then
    assert len(candles) == 600
