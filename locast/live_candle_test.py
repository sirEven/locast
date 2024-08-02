import asyncio

from dydx_v4_client.indexer.candles_resolution import CandlesResolution
from dydx_v4_client.indexer.socket.websocket import IndexerSocket
from dydx_v4_client.network import TESTNET

ETH_USD = "ETH-USD"


def handle_message(ws: IndexerSocket, message: dict):
    if message["type"] == "connected":
        ws.candles.subscribe(ETH_USD, CandlesResolution.ONE_MINUTE)

    if message["type"] == "subscribed":
        print(f"Subscription successful ({message['channel']}, {message['id']}).")

    if message["type"] == "channel_batch_data":
        if candle_dict := message["contents"][0]:
            print(f"Active candle: {candle_dict['startedAt']}")


async def test():
    await IndexerSocket(TESTNET.websocket_indexer, on_message=handle_message).connect()


asyncio.run(test())
