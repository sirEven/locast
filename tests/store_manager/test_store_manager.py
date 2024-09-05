import pytest
from sir_utilities.date_time import string_to_datetime

from locast.candle.candle_utility import CandleUtility as cu
from locast.candle.exchange import Exchange
from locast.candle.resolution import ResolutionDetail, Seconds
from locast.candle_storage.sql.sqlite_candle_storage import SqliteCandleStorage
from locast.store_manager.store_manager import StoreManager


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

    start_date = string_to_datetime("2024-08-01T00:00:00.000Z")
    end_date = cu.normalized_now(resolution.seconds)
    # when
    await manager.create_cluster(market, resolution, start_date)

    # then
    expected_amount = cu.amount_of_candles_in_range(
        start_date,
        end_date,
        resolution.seconds,
    )
    cluster_info = await storage.get_cluster_info(exchange, market, resolution.seconds)

    assert cluster_info
    assert cluster_info.is_uptodate
    assert cluster_info.amount == expected_amount
    assert cluster_info.tail.started_at == start_date
