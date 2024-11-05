import asyncio

from dydx_v4_client.indexer.rest.indexer_client import IndexerClient  # type: ignore
from dydx_v4_client.network import make_mainnet  # type: ignore
from locast.candle.dydx.dydx_resolution import DydxResolution
from locast.candle_fetcher.dydx.candle_fetcher.dydx_candle_fetcher import (
    DydxCandleFetcher,
)
from locast.candle_fetcher.dydx.api_fetcher.dydx_v4_fetcher import DydxV4Fetcher
from locast.candle.candle_utility import CandleUtility as cu

MAINNET = make_mainnet(  # type: ignore
    rest_indexer="https://indexer.dydx.trade/",
    websocket_indexer="wss://indexer.dydx.trade/v4/ws",
    node_url="dydx-ops-rpc.kingnodes.com:443",
)


async def main() -> None:
    res = DydxResolution.FIFTEEN_MINUTES
    market = "DOGE-USD"
    dydx_v4_fetcher = DydxV4Fetcher(IndexerClient(MAINNET.rest_indexer))
    fetcher = DydxCandleFetcher(dydx_v4_fetcher)

    horizon = await fetcher.find_horizon(market, res)
    print(f"horizon: {horizon}")

    horizon_plus_one = cu.add_one_resolution(horizon, res)
    horizon_minus_one = cu.subtract_n_resolutions(horizon, res, 1)
    horizon_minus_two = cu.subtract_n_resolutions(horizon, res, 2)
    oldest_candle = await fetcher.fetch_candles(
        market,
        res,
        horizon,
        horizon_plus_one,
    )

    one_older = await fetcher.fetch_candles(
        market,
        res,
        horizon_minus_one,
        horizon,
    )

    two_older = await fetcher.fetch_candles(
        market,
        res,
        horizon_minus_two,
        horizon_minus_one,
    )

    print("Oldest:")
    print(oldest_candle)
    print("One older:")
    print(one_older)
    print("Two older:")
    print(two_older)


asyncio.run(main())
