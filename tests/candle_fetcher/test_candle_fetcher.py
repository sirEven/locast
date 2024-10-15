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
from tests.helper.candle_mockery.dydx_candle_backend_mock import DydxCandleBackendMock
from tests.helper.parametrization.list_of_resolution_details import resolutions

from tests.helper.fixture_helpers import get_typed_fixture


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


# TODO: How to write the test in such a way, that we can tell the received fetcher, its api_fetcher mock
# shall produce candle violations in order to test log output? chad chippity suggests dynamic test creation...
# An other Idea is to finally mock candles as a fake backend, such that it can be used as a fixture.
# This way we could direct the client and indexer mocks candle creation towards that backend, and switch its mode from normal
# to including missing candles when needed.
@pytest.mark.parametrize("candle_fetcher_mock", mocked_candle_fetchers)
@pytest.mark.asyncio
async def test_fetch_cluster_prints_progress_correctly(
    request: pytest.FixtureRequest,
    capsys: pytest.CaptureFixture[str],
    candle_fetcher_mock: str,
) -> None:
    # given
    fetcher = get_typed_fixture(request, candle_fetcher_mock, DydxCandleFetcher)
    fetcher.log_progress = True
    res = DydxResolution.ONE_MINUTE
    amount_back = 1200
    market = "ETH-USD"

    now_rounded = cu.norm_date(now_utc_iso(), res)
    start_date = now_rounded - timedelta(seconds=res.seconds * amount_back)

    # when
    _ = await fetcher.fetch_candles_up_to_now(market, res, start_date)

    # then
    out, _ = capsys.readouterr()
    assert f"of {amount_back} candles fetched." in out
    assert f"🚛 {amount_back} of {amount_back} candles fetched. ✅" in out


@pytest.mark.parametrize("candle_fetcher_mock", mocked_candle_fetchers)
@pytest.mark.asyncio
async def test_fetch_cluster_prints_missing_candles_correctly(
    request: pytest.FixtureRequest,
    capsys: pytest.CaptureFixture[str],
    dydx_candle_backend_mock: DydxCandleBackendMock,
    candle_fetcher_mock: str,
) -> None:
    # given
    backend = dydx_candle_backend_mock
    n_missing = 5
    backend.missing_random_candles = n_missing

    fetcher = get_typed_fixture(request, candle_fetcher_mock, DydxCandleFetcher)
    fetcher.log_progress = True
    res = DydxResolution.ONE_MINUTE
    amount_back = 120
    market = "ETH-USD"

    now_rounded = cu.norm_date(now_utc_iso(), res)
    start_date = now_rounded - timedelta(seconds=res.seconds * amount_back)

    # when
    _ = await fetcher.fetch_candles_up_to_now(market, res, start_date)

    # then
    out, _ = capsys.readouterr()
    assert "" in out  # TODO: Additional test for batch boundry errors.
    assert "🚨 Attention:" in out
    assert out.count("❌ Candle missing:") == n_missing


# TODO consolidated:
# a) test batch boundary violations (3 versions: on batch start, on batch end, on both)
# b) test complete fetch boundary violations: (5 versions: missing the newest, missing multiple newest, missing the oldest, missing multiple oldest, and all together)

# TODO: This test wont work yet and has 2 follow up tests (batch start and both togeter)
# TODO: Think of the edge case, that the very first candle of the very first batch is missing. This is not handled by overlapping checks.
# @pytest.mark.parametrize("candle_fetcher_mock", mocked_candle_fetchers)
# @pytest.mark.asyncio
# async def test_fetch_cluster_prints_violations_on_batch_end_correctly(
#     request: pytest.FixtureRequest,
#     capsys: pytest.CaptureFixture[str],
#     dydx_candle_backend_mock: DydxCandleBackendMock,
#     candle_fetcher_mock: str,
# ) -> None:
#     # given
#     backend = dydx_candle_backend_mock
#     backend.missing_candles_on_batch_end = True

#     fetcher = get_typed_fixture(request, candle_fetcher_mock, DydxCandleFetcher)
#     fetcher.log_progress = True
#     res = DydxResolution.ONE_MINUTE
#     amount_back = 120
#     market = "ETH-USD"

#     now_rounded = cu.norm_date(now_utc_iso(), res)
#     start_date = now_rounded - timedelta(seconds=res.seconds * amount_back)

#     # when
#     _ = await fetcher.fetch_candles_up_to_now(market, res, start_date)

#     # then
#     out, _ = capsys.readouterr()
#     assert "" in out  # TODO: batch boundry errors.
#     assert "🚨 Attention:" in out
#     assert "❌ 1 missing between" in out
#     assert "❌ 2 missing between" in out

#     print(out)
