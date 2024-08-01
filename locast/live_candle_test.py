import asyncio

from dydx_v4_client.indexer.candles_resolution import CandlesResolution
from dydx_v4_client.indexer.socket.websocket import IndexerSocket
from dydx_v4_client.network import TESTNET

ETH_USD = "ETH-USD"


def handle_message(ws: IndexerSocket, message: dict):
    if message["type"] == "connected":
        ws.candles.subscribe(ETH_USD, CandlesResolution.ONE_MINUTE)
    print(message)
    print("")


async def test():
    await IndexerSocket(TESTNET.websocket_indexer, on_message=handle_message).connect()


asyncio.run(test())
