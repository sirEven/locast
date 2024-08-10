from datetime import timedelta
import pytest

from sir_utilities.date_time import now_utc_iso, datetime_to_string


from locast.candle.candle_utility import CandleUtility as cu
from locast.candle.dydx.dydx_resolution import DydxResolution
from locast.candle.exchange import Exchange
from locast.candle_fetcher.dydx.dydx_candle_fetcher import DydxCandleFetcher


@pytest.mark.asyncio
async def test_v4_fetch_600_historic_candles_testnet(
    dydx_v4_candle_fetcher_testnet: DydxCandleFetcher,
) -> None:
    # given
    fetcher = dydx_v4_candle_fetcher_testnet
    start = "2024-04-01T00:00:00.000Z"
    end = "2024-04-01T10:00:00.000Z"

    # when
    candles = await fetcher.fetch_candles(
        Exchange.DYDX_V4,
        "ETH-USD",
        DydxResolution.ONE_MINUTE.notation,
        start,
        end,
    )

    # then
    assert len(candles) == 600


@pytest.mark.asyncio
async def test_v4_fetch_600_historic_candles_mainnet(
    dydx_v4_candle_fetcher_mainnet: DydxCandleFetcher,
) -> None:
    # given
    fetcher = dydx_v4_candle_fetcher_mainnet
    start = "2024-06-01T00:00:00.000Z"
    end = "2024-06-01T10:00:00.000Z"

    # when
    candles = await fetcher.fetch_candles(
        Exchange.DYDX_V4,
        "ETH-USD",
        DydxResolution.ONE_MINUTE.notation,
        start,
        end,
    )

    # then
    assert len(candles) == 600


# https://indexer.dydx.trade/v4/v4/candles/perpetualMarkets/ETH-USD?resolution=5MINS&fromISO=2024-07-23%2007:45:00+0000&toISO=2024-08-09T16:25:00.000000Z
@pytest.mark.asyncio
async def test_v4_fetch_cluster_is_up_to_date(
    dydx_v4_candle_fetcher_mainnet: DydxCandleFetcher,
) -> None:
    # given
    fetcher = dydx_v4_candle_fetcher_mainnet

    res = DydxResolution.FIVE_MINUTES
    amount_back = 50
    now_rounded = cu.norm_date(now_utc_iso(), res.seconds)
    start_date = now_rounded - timedelta(seconds=res.seconds * amount_back)
    # TODO: Think of a way to check if a fetch that takes longer than 1 res, leads
    # to correct candles (gap filled) - probably needs integration test against mainnet api
    # when
    candles = await fetcher.fetch_cluster(
        Exchange.DYDX_V4,
        "ETH-USD",
        res.notation,
        datetime_to_string(start_date),
    )

    # then
    assert len(candles) == 50
