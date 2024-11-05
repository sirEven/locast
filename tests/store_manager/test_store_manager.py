from datetime import timedelta
import pytest

from locast.candle.candle_utility import CandleUtility as cu
from locast.candle.exchange import Exchange
from locast.candle.exchange_resolution import ResolutionDetail, Seconds
from locast.candle_storage.sql.sqlite_candle_storage import SqliteCandleStorage
from locast.store_manager.store_manager import (
    ExistingClusterException,
    MissingClusterException,
    StoreManager,
)
from tests.helper.candle_mockery.mock_dydx_v4_candles import mock_dydx_v4_candle_range


# FIXME: WIP - BACKEND MOCK NOT HANDLING HORIZON
@pytest.mark.asyncio
async def test_create_cluster_results_in_correct_cluster_state(
    store_manager_mock_memory: StoreManager,
    sqlite_candle_storage_memory: SqliteCandleStorage,
) -> None:
    # given
    manager = store_manager_mock_memory
    storage = sqlite_candle_storage_memory

    exchange = Exchange.DYDX_V4
    market = "ETH-USD"
    resolution = ResolutionDetail(Seconds.FOUR_HOURS, "4HOURS")

    end_date = cu.normalized_now(resolution)
    start_date = cu.subtract_n_resolutions(end_date, resolution, 10)

    # when
    await manager.create_cluster(market, resolution, start_date)

    # then
    expected_amount = cu.amount_of_candles_in_range(
        start_date,
        end_date,
        resolution,
    )

    info = await storage.get_cluster_info(exchange, market, resolution)

    assert info.newest_candle and info.oldest_candle
    assert info.is_uptodate
    assert info.size == expected_amount
    assert info.oldest_candle.started_at == start_date


@pytest.mark.asyncio
async def test_create_cluster_results_in_error(
    store_manager_mock_memory: StoreManager,
) -> None:
    # given a cluster is already present
    manager = store_manager_mock_memory

    market = "ETH-USD"
    resolution = ResolutionDetail(Seconds.FOUR_HOURS, "4HOURS")

    start_date = cu.subtract_n_resolutions(
        cu.normalized_now(resolution),
        resolution,
        10,
    )
    await manager.create_cluster(market, resolution, start_date)

    # when the same cluster is created again
    with pytest.raises(ExistingClusterException):
        await manager.create_cluster(market, resolution, start_date)


@pytest.mark.asyncio
async def test_create_cluster_replaces_existing_cluster(
    store_manager_mock_memory: StoreManager,
    sqlite_candle_storage_memory: SqliteCandleStorage,
) -> None:
    # given
    manager = store_manager_mock_memory
    storage = sqlite_candle_storage_memory

    exchange = Exchange.DYDX_V4
    market = "ETH-USD"
    resolution = ResolutionDetail(Seconds.FOUR_HOURS, "4HOURS")

    end_date = cu.normalized_now(resolution)
    start_date = cu.subtract_n_resolutions(end_date, resolution, 10)

    await manager.create_cluster(market, resolution, start_date)

    # when replace flag is set
    await manager.create_cluster(
        market,
        resolution,
        start_date,
        replace_existing_cluster=True,
    )

    # then
    expected_amount = cu.amount_of_candles_in_range(
        start_date,
        end_date,
        resolution,
    )

    info = await storage.get_cluster_info(exchange, market, resolution)

    assert info.newest_candle and info.oldest_candle
    assert info.is_uptodate
    assert info.size == expected_amount
    assert info.oldest_candle.started_at == start_date


@pytest.mark.asyncio
async def test_update_cluster_results_in_uptodate_cluster(
    store_manager_mock_memory: StoreManager,
    sqlite_candle_storage_memory: SqliteCandleStorage,
) -> None:
    # given storage containing out of date cluster
    manager = store_manager_mock_memory
    storage = sqlite_candle_storage_memory

    exchange = Exchange.DYDX_V4
    market = "ETH-USD"
    resolution = ResolutionDetail(Seconds.FOUR_HOURS, "4HOURS")
    res_sec = resolution.seconds

    start_date = cu.normalized_now(resolution) - timedelta(seconds=res_sec * 10)
    end_date = cu.normalized_now(resolution) - timedelta(seconds=res_sec * 5)
    old_cluster = mock_dydx_v4_candle_range(market, resolution, start_date, end_date)

    await storage.store_candles(old_cluster)
    old_info = await storage.get_cluster_info(exchange, market, resolution)

    # when
    await manager.update_cluster(exchange, market, resolution)

    # then
    info = await storage.get_cluster_info(exchange, market, resolution)

    assert old_info
    assert not old_info.is_uptodate

    assert info.is_uptodate


@pytest.mark.asyncio
async def test_update_cluster_results_in_valid_cluster(
    store_manager_mock_memory: StoreManager,
    sqlite_candle_storage_memory: SqliteCandleStorage,
) -> None:
    # given storage containing out of date cluster
    manager = store_manager_mock_memory
    storage = sqlite_candle_storage_memory

    exchange = Exchange.DYDX_V4
    market = "ETH-USD"
    resolution = ResolutionDetail(Seconds.FOUR_HOURS, "4HOURS")
    res_sec = resolution.seconds

    start_date = cu.normalized_now(resolution) - timedelta(seconds=res_sec * 10)
    end_date = cu.normalized_now(resolution) - timedelta(seconds=res_sec * 5)

    old_cluster = mock_dydx_v4_candle_range(market, resolution, start_date, end_date)

    await storage.store_candles(old_cluster)

    # when
    await manager.update_cluster(exchange, market, resolution)

    # then
    info = await storage.get_cluster_info(exchange, market, resolution)
    cluster = await storage.retrieve_cluster(exchange, market, resolution)
    cluster_dates = [candle.started_at for candle in cluster]

    cu.assert_candle_unity(cluster)
    assert len(cu.detect_missing_dates(cluster_dates, resolution)) == 0
    assert info.newest_candle
    assert cu.is_newest_valid_candle(info.newest_candle)
    assert cluster[0] == info.newest_candle
    assert cluster[-1] == info.oldest_candle


@pytest.mark.asyncio
async def test_update_cluster_results_in_error(
    store_manager_mock_memory: StoreManager,
) -> None:
    # given storage containing no cluster
    manager = store_manager_mock_memory

    exchange = Exchange.DYDX_V4
    market = "ETH-USD"
    resolution = ResolutionDetail(Seconds.FOUR_HOURS, "4HOURS")

    # when & then
    with pytest.raises(MissingClusterException):
        await manager.update_cluster(exchange, market, resolution)


@pytest.mark.asyncio
async def test_update_cluster_results_in_no_error_when_cluster_is_uptodate(
    store_manager_mock_memory: StoreManager,
) -> None:
    # given up to date cluster
    manager = store_manager_mock_memory

    exchange = Exchange.DYDX_V4
    market = "ETH-USD"
    resolution = ResolutionDetail(Seconds.FOUR_HOURS, "4HOURS")
    start_date = cu.normalized_now(resolution) - timedelta(
        seconds=resolution.seconds * 10
    )
    await manager.create_cluster(market, resolution, start_date)

    # when & then
    await manager.update_cluster(exchange, market, resolution)


@pytest.mark.asyncio
async def test_delete_cluster_results_in_error(
    store_manager_mock_memory: StoreManager,
) -> None:
    # given storage containing no cluster
    manager = store_manager_mock_memory

    exchange = Exchange.DYDX_V4
    market = "ETH-USD"
    resolution = ResolutionDetail(Seconds.FOUR_HOURS, "4HOURS")

    # when & then
    with pytest.raises(MissingClusterException):
        await manager.delete_cluster(exchange, market, resolution)


@pytest.mark.asyncio
async def test_retrieve_cluster_results_in_error(
    store_manager_mock_memory: StoreManager,
) -> None:
    # given storage containing no cluster
    manager = store_manager_mock_memory

    exchange = Exchange.DYDX_V4
    market = "ETH-USD"
    resolution = ResolutionDetail(Seconds.FOUR_HOURS, "4HOURS")

    # when & then
    with pytest.raises(MissingClusterException):
        await manager.retrieve_cluster(exchange, market, resolution)


@pytest.mark.asyncio
async def test_retrieve_cluster_results_in_correct_cluster(
    store_manager_mock_memory: StoreManager,
    sqlite_candle_storage_memory: SqliteCandleStorage,
) -> None:
    # given
    manager = store_manager_mock_memory
    storage = sqlite_candle_storage_memory

    exchange = Exchange.DYDX_V4
    market = "ETH-USD"
    resolution = ResolutionDetail(Seconds.FOUR_HOURS, "4HOURS")

    end_date = cu.normalized_now(resolution)
    start_date = cu.subtract_n_resolutions(end_date, resolution, 10)
    await manager.create_cluster(market, resolution, start_date)

    # when
    cluster = await manager.retrieve_cluster(exchange, market, resolution)

    # then
    info = await storage.get_cluster_info(exchange, market, resolution)
    cluster_dates = [candle.started_at for candle in cluster]

    assert cluster[0] == info.newest_candle
    assert cluster[-1] == info.oldest_candle
    cu.assert_candle_unity(cluster)
    assert len(cu.detect_missing_dates(cluster_dates, resolution)) == 0


@pytest.mark.asyncio
async def test_get_cluster_info_returns_correctly(
    store_manager_mock_memory: StoreManager,
) -> None:
    # given
    manager = store_manager_mock_memory

    exchange = Exchange.DYDX_V4
    market = "ETH-USD"
    resolution = ResolutionDetail(Seconds.FOUR_HOURS, "4HOURS")

    end_date = cu.normalized_now(resolution)
    start_date = cu.subtract_n_resolutions(end_date, resolution, 10)
    await manager.create_cluster(market, resolution, start_date)

    # when
    info = await manager.get_cluster_info(exchange, market, resolution)

    # then
    expected_cluster = await manager.retrieve_cluster(exchange, market, resolution)
    assert info.newest_candle == expected_cluster[0]
    assert info.oldest_candle == expected_cluster[-1]
