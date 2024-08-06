from typing import AsyncGenerator
import pytest_asyncio

from locast.candle.dydx.dydx_resolution import DydxResolution
from locast.live_candle.dydx.dydx_live_candle import DydxV4LiveCandle
from dydx_v4_client.network import TESTNET  # type: ignore

ETH_USD = "ETH-USD"
BTC_USD = "BTC-USD"
ONE_MIN = DydxResolution.ONE_MINUTE


@pytest_asyncio.fixture  # type: ignore
async def dydx_v4_live_candle() -> AsyncGenerator[DydxV4LiveCandle, None]:
    m_p_r = {
        ONE_MIN.notation: [ETH_USD, BTC_USD],
    }
    live_candle = DydxV4LiveCandle(
        host_url=TESTNET.websocket_indexer,
        markets_per_resolution=m_p_r,
    )

    yield live_candle
    await live_candle.stop()
