from datetime import timedelta
from typing import Any, Dict
import pytest

from sir_utilities.date_time import now_utc_iso, string_to_datetime

from locast.candle.candle_utility import CandleUtility as cu
from locast.candle.resolution import ResolutionDetail
from locast.candle_fetcher.candle_fetcher import CandleFetcher

from locast.candle_fetcher.exceptions import APIException
from tests.helper.candle_mockery.candle_backend_mock import CandleBackendMock
from tests.helper.parametrization.list_of_resolution_details import resolutions

from tests.helper.fixture_helpers import get_typed_fixture

# TODO: Incorporate backend mock protocol to get rid of dydx type DydxCandleBackendMock
# COLLABORATION: Add additional mock implementations to this dictionary to include them in the unit test suite:
# - The key is the name of the mocked candle fetcher fixture
# - amount_back is the number of candles to be fetched (One candle less than two full batches; e.g.: 199 for batch size 100).
# - backend_mock is the name of the mocked backend in use for this mocked candle fetcher

mocked_candle_fetchers: Dict[str, Any] = {
    "dydx_v3_candle_fetcher_mock": {
        "amount_back": 199,
        "backend_mock": "dydx_candle_backend_mock",
    },
    "dydx_v4_candle_fetcher_mock": {
        "amount_back": 1999,
        "backend_mock": "dydx_candle_backend_mock",
    },
}

resolutions_reduced = resolutions[:-2]


@pytest.mark.parametrize("resolution", resolutions_reduced)
@pytest.mark.parametrize("candle_fetcher_mock", list(mocked_candle_fetchers.keys()))
@pytest.mark.asyncio
async def test_fetch_fixed_amount_of_candles(
    request: pytest.FixtureRequest,
    candle_fetcher_mock: str,
    resolution: ResolutionDetail,
) -> None:
    # given
    fetcher = get_typed_fixture(request, candle_fetcher_mock, CandleFetcher)
    res = resolution
    start = string_to_datetime("2024-04-01T00:00:00.000Z")
    end = string_to_datetime("2024-04-01T05:00:00.000Z")

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


@pytest.mark.parametrize("candle_fetcher_mock", list(mocked_candle_fetchers.keys()))
@pytest.mark.asyncio
async def test_fetch_cluster_is_up_to_date(
    request: pytest.FixtureRequest,
    candle_fetcher_mock: str,
) -> None:
    # given
    fetcher = get_typed_fixture(request, candle_fetcher_mock, CandleFetcher)
    res = resolutions_reduced[0]
    amount_back = mocked_candle_fetchers[candle_fetcher_mock].get("amount_back")
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


@pytest.mark.parametrize("candle_fetcher_mock", list(mocked_candle_fetchers.keys()))
@pytest.mark.asyncio
async def test_fetch_cluster_raises_api_exception(
    request: pytest.FixtureRequest,
    candle_fetcher_mock: str,
) -> None:
    # given
    fetcher = get_typed_fixture(request, candle_fetcher_mock, CandleFetcher)
    res = resolutions_reduced[0]
    amount_back = mocked_candle_fetchers[candle_fetcher_mock].get("amount_back")
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


@pytest.mark.parametrize("candle_fetcher_mock", list(mocked_candle_fetchers.keys()))
@pytest.mark.asyncio
async def test_fetch_cluster_prints_progress_correctly(
    request: pytest.FixtureRequest,
    capsys: pytest.CaptureFixture[str],
    candle_fetcher_mock: str,
) -> None:
    # given
    fetcher = get_typed_fixture(request, candle_fetcher_mock, CandleFetcher)
    fetcher.log_progress = True
    res = resolutions_reduced[0]
    amount_back = mocked_candle_fetchers[candle_fetcher_mock].get("amount_back")
    market = "ETH-USD"

    now_rounded = cu.norm_date(now_utc_iso(), res)
    start_date = now_rounded - timedelta(seconds=res.seconds * amount_back)

    # when
    _ = await fetcher.fetch_candles_up_to_now(market, res, start_date)

    # then
    out, _ = capsys.readouterr()
    assert f"of {amount_back} candles fetched." in out
    assert f"🚛 {amount_back} of {amount_back} candles fetched. ✅" in out


# TODO: Propagate this change to the rest of the tests.
@pytest.mark.parametrize("candle_fetcher_mock", list(mocked_candle_fetchers.keys()))
@pytest.mark.asyncio
async def test_fetch_cluster_prints_missing_candles_correctly(
    request: pytest.FixtureRequest,
    capsys: pytest.CaptureFixture[str],
    candle_fetcher_mock: str,
) -> None:
    # given
    backend_mock_str = mocked_candle_fetchers[candle_fetcher_mock]["backend_mock"]
    backend = get_typed_fixture(request, backend_mock_str, CandleBackendMock)
    n_missing = 5
    backend.missing_random_candles = n_missing

    fetcher = get_typed_fixture(request, candle_fetcher_mock, CandleFetcher)
    fetcher.log_progress = True
    res = resolutions_reduced[0]
    amount_back = mocked_candle_fetchers[candle_fetcher_mock].get("amount_back")
    market = "ETH-USD"

    now_rounded = cu.norm_date(now_utc_iso(), res)
    start_date = now_rounded - timedelta(seconds=res.seconds * amount_back)

    # when
    _ = await fetcher.fetch_candles_up_to_now(market, res, start_date)

    # then
    out, _ = capsys.readouterr()
    assert "" in out
    assert "🚨 Attention:" in out
    assert out.count("❌ Candle missing:") == n_missing


@pytest.mark.parametrize("candle_fetcher_mock", list(mocked_candle_fetchers.keys()))
@pytest.mark.asyncio
async def test_fetch_cluster_prints_missing_candles_on_batch_newest_edge_correctly(
    request: pytest.FixtureRequest,
    capsys: pytest.CaptureFixture[str],
    dydx_candle_backend_mock: CandleBackendMock,
    candle_fetcher_mock: str,
) -> None:
    # given
    backend = dydx_candle_backend_mock
    n_missing = 5
    backend.missing_candles_on_batch_newest_edge = n_missing

    fetcher = get_typed_fixture(request, candle_fetcher_mock, CandleFetcher)
    fetcher.log_progress = True
    res = resolutions_reduced[0]
    amount_back = mocked_candle_fetchers[candle_fetcher_mock].get("amount_back")
    market = "ETH-USD"

    now_rounded = cu.norm_date(now_utc_iso(), res)
    start_date = now_rounded - timedelta(seconds=res.seconds * amount_back)

    # when
    _ = await fetcher.fetch_candles_up_to_now(market, res, start_date)

    # then
    out, _ = capsys.readouterr()
    assert "" in out
    assert "🚨 Attention:" in out
    assert out.count("❌ Candle missing:") == n_missing
