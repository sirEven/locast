from datetime import timedelta
import pytest

from sir_utilities.date_time import now_utc_iso, string_to_datetime
from locast.candle.candle_utility import CandleUtility as cu
from locast.candle.dydx.dydx_resolution import DydxResolution
from locast.candle_fetcher.dydx.dydx_v4_candle_fetcher import DydxV4CandleFetcher


@pytest.mark.asyncio
async def test_v4_fetch_600_historic_candles(
    mock_dydx_v4_candle_fetcher: DydxV4CandleFetcher,
) -> None:
    # given
    fetcher = mock_dydx_v4_candle_fetcher
    res = DydxResolution.ONE_MINUTE
    start = string_to_datetime("2024-04-01T00:00:00.000Z")
    end = string_to_datetime("2024-04-01T10:00:00.000Z")

    # when
    candles = await fetcher.fetch_candles(
        "ETH-USD",
        res.notation,
        start,
        end,
    )

    # then
    assert len(candles) == 600
    assert candles[-1].started_at == start
    assert candles[0].started_at == end - timedelta(seconds=res.seconds)


@pytest.mark.asyncio
async def test_v4_fetch_cluster_is_up_to_date(
    mock_dydx_v4_candle_fetcher: DydxV4CandleFetcher,
) -> None:
    # given
    fetcher = mock_dydx_v4_candle_fetcher
    res = DydxResolution.ONE_MINUTE
    amount_back = 5000
    now_rounded = cu.norm_date(now_utc_iso(), res.seconds)
    start_date = now_rounded - timedelta(seconds=res.seconds * amount_back)

    # when
    candles = await fetcher.fetch_candles_up_to_now(
        "ETH-USD",
        res.notation,
        start_date,
    )

    # then
    cu.assert_candle_unity(candles)
    cu.assert_chronologic_order(candles)
    assert cu.is_newest_valid_candle(candles[0])
    assert len(candles) >= amount_back
