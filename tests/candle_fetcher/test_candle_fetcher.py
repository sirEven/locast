from datetime import timedelta
import pytest

from sir_utilities.date_time import now_utc_iso, string_to_datetime

from locast.candle.candle_utility import CandleUtility as cu
from locast.candle.dydx.dydx_resolution import DydxResolution
from locast.candle.resolution import ResolutionDetail
from locast.candle_fetcher.dydx.candle_fetcher.dydx_candle_fetcher import (
    DydxCandleFetcher,
)

from locast.candle_fetcher.exceptions import APIException
from tests.helper.parametrization.list_of_resolution_details import resolutions

from tests.conftest import get_typed_fixture


# NOTE: Add additional mock implementations into this list, to include them in the unit test suite.
mocked_candle_fetchers = ["dydx_v3_candle_fetcher_mock", "dydx_v4_candle_fetcher_mock"]
resolutions_reduced = resolutions[:-2]


@pytest.mark.parametrize("resolution", resolutions_reduced)
@pytest.mark.parametrize("candle_fetcher_mock", mocked_candle_fetchers)
@pytest.mark.asyncio
async def test_fetch_600_candles(
    request: pytest.FixtureRequest,
    candle_fetcher_mock: str,
    resolution: ResolutionDetail,
) -> None:
    # given
    fetcher = get_typed_fixture(request, candle_fetcher_mock, DydxCandleFetcher)
    res = resolution
    start = string_to_datetime("2024-04-01T00:00:00.000Z")
    end = string_to_datetime("2024-04-01T10:00:00.000Z")

    # when
    candles = await fetcher.fetch_candles(
        "ETH-USD",
        res,
        start,
        end,
    )

    # then
    amount = cu.amount_of_candles_in_range(start, end, res)
    assert len(candles) == amount
    assert candles[-1].started_at == start
    assert candles[0].started_at == end - timedelta(seconds=res.seconds)


@pytest.mark.parametrize("candle_fetcher_mock", mocked_candle_fetchers)
@pytest.mark.asyncio
async def test_fetch_cluster_is_up_to_date(
    request: pytest.FixtureRequest,
    candle_fetcher_mock: str,
) -> None:
    # given
    fetcher = get_typed_fixture(request, candle_fetcher_mock, DydxCandleFetcher)
    res = DydxResolution.ONE_MINUTE
    amount_back = 2500
    now_rounded = cu.norm_date(now_utc_iso(), res)
    start_date = now_rounded - timedelta(seconds=res.seconds * amount_back)

    # when
    candles = await fetcher.fetch_candles_up_to_now(
        "ETH-USD",
        res,
        start_date,
    )

    # then
    cu.assert_candle_unity(candles)
    assert cu.is_newest_valid_candle(candles[0])


@pytest.mark.parametrize("candle_fetcher_mock", mocked_candle_fetchers)
@pytest.mark.asyncio
async def test_fetch_cluster_raises_api_exception(
    request: pytest.FixtureRequest,
    candle_fetcher_mock: str,
) -> None:
    # given
    fetcher = get_typed_fixture(request, candle_fetcher_mock, DydxCandleFetcher)
    res = DydxResolution.ONE_MINUTE
    amount_back = 2500
    market = "INVALID_MARKET"
    now_rounded = cu.norm_date(now_utc_iso(), res)
    start_date = now_rounded - timedelta(seconds=res.seconds * amount_back)

    # when & then
    with pytest.raises(APIException) as e:
        print(e)
        _ = await fetcher.fetch_candles_up_to_now(
            market,
            res,
            start_date,
        )
