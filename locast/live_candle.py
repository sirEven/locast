# Stuff that will be needed down the line:
# - Getting candles via websocket (live) ✅
# - as well as via api requests (historic) ✅
# -- build basic infrastructure to fetch historic candles cleanly --
# -- build basic subscribe and unsubscribe from live candle update --
# - Opening & closing a position
# - Querying position data such as pnl...
# - Querying account balance

import asyncio
from typing import Any, Dict

from dydx_v4_client.indexer.socket.websocket import CandlesResolution, IndexerSocket  # type: ignore
from dydx_v4_client.network import TESTNET  # type: ignore

from locast.candle.candle import Candle
from locast.candle.exchange import Exchange
from locast.candle.exchange_candle_mapper import ExchangeCandleMapper  # type: ignore


# logging.basicConfig(level=logging.DEBUG)

TEST_ADDRESS = "dydx1ms05ewt4my7t2w62lz52xv65y5f42ttn4zcevp"
ETH_USD = "ETH-USD"
BTC_USD = "BTC-USD"
LINK_USD = "LINK-USD"


# This provides a live updated price candle where every change is sent with immediate irregular & regular messages
# The regular websocket messages simply announce the new candle from current timestamp corresponding to its startedAt
class DydxV4LiveCandle:
    def __init__(
        self,
        exchange: Exchange,
        markets_resolutions: Dict[str, CandlesResolution],
    ) -> None:
        self._exchange = exchange
        self._markets_resolutions = markets_resolutions
        self._newest_ended_candle: Dict[str, Candle] = {}
        self._active_candle: Dict[str, Candle] = {}

    def get_active_candle(self, market: str) -> Candle | None:
        return self._active_candle.get(market)

    def get_newest_ended_candle(self, market: str) -> Candle | None:
        return self._newest_ended_candle.get(market)

    def handle_live_candle_message(self, ws: IndexerSocket, message: Dict[str, Any]):
        if message["type"] == "connected":
            for market, res in self._markets_resolutions.items():
                print(f"Subscribing to {res.value} candles for {market}.")
                ws.candles.subscribe(market, res)  # type: ignore

        if message["type"] == "subscribed":
            print(f"Subscription successful ({message['channel']}, {message['id']}).")

        if message["type"] == "channel_batch_data":
            if candle_dict := message["contents"][0]:
                new_candle = ExchangeCandleMapper.dict_to_candle(
                    self._exchange,
                    candle_dict,
                )
                if current_candle := self._active_candle.get(new_candle.market):
                    if current_candle.started_at < new_candle.started_at:
                        # New candle started -> shift active to ended
                        self._newest_ended_candle[new_candle.market] = current_candle
                # Update to the active candle -> update active
                self._active_candle[new_candle.market] = new_candle


async def test():
    live_candle = DydxV4LiveCandle(
        exchange=Exchange.DYDX_V4,
        markets_resolutions={
            ETH_USD: CandlesResolution.ONE_MINUTE,
            BTC_USD: CandlesResolution.FIVE_MINUTES,
        },
    )
    await IndexerSocket(
        TESTNET.websocket_indexer,
        on_message=live_candle.handle_live_candle_message,  # type: ignore
    ).connect()


asyncio.run(test())
