# Stuff that will be needed down the line:
# - Getting candles via websocket (live) ✅
# - as well as via api requests (historic) ✅
# - sqlite database to store & retrieve candles
# -- build basic infrastructure to fetch historic candles cleanly --
# -- build basic subscribe and unsubscribe from live candle update --

# - For another project:
#   - Opening & closing a position
#   - Querying position data such as pnl...
#   - Querying account balance

import asyncio
import logging
import threading
from typing import Any, Dict, List

from dydx_v4_client.indexer.socket.websocket import IndexerSocket, CandlesResolution  # type: ignore

from locast.candle.candle import Candle
from locast.candle.exchange import Exchange
from locast.candle.exchange_candle_mapper import ExchangeCandleMapper

logging.basicConfig(level=logging.DEBUG)

"""
The idea of this part of the LOCAST component is to have the live candle turn on at the begining of execution, either by itself within init, or by the glue project
that calls its start function. And stop function at shut down. 
What can be considered unnecessary is dynamic subscribing and unsubscribing to certain markets - instead we could pause
publishing those candles if desired. But even that might be unnecessary. We should think about what exactly we would want to 
pause, once a position has beend opened. Naturally we would keep candles being created and published but would simply stop forming fresh 
predictions.
Also we should update (or create) all candle clusters of the corresponding markets and resolutions that we also start as live candles.
The orchestration of this would be implemented in glue project, meaning Locast only has very rudimentary API methods:
- create cluster
- update cluster
- start live candle
- stop live candle

This guarantees, that it can be reused in model training project as well where different glue code is needed but same basic functionality.
For example: create / update clusters, train models. Whereas glue project would want to just start a live candle and feed it into prediction module.
Later on maybe have glue code updated to incorporate some sort of regularily update clusters (every n resolutions), retrain models etc, such that prediction module always
loads the latest trained model before performing predictions.
"""


class DydxV4LiveCandle:
    def __init__(
        self,
        host_url: str,
        resolutions_for_markets: Dict[str, str],
    ) -> None:
        self._ws = IndexerSocket(host_url, on_message=self.handle_message)  # type: ignore
        self._exchange = Exchange.DYDX_V4
        self._resolutions = resolutions_for_markets
        self._market_candles: Dict[str, List[Candle]] = {}
        self.subscriptions: Dict[str, bool] = {}

    async def connect(self) -> None:
        # NOTE: ._ws.connect() is a blocking async function call that needs to be wrapped
        await self._ws.connect()  # type: ignore

    def wrap_async_func(self) -> None:
        asyncio.run(self.connect())

    def start_live_candle_connection(self) -> None:
        t = threading.Thread(target=self.wrap_async_func)
        t.start()

    def get_active_candle(self, market: str) -> Candle | None:
        if candles := self._market_candles.get(market):
            return candles[0]

    def get_newest_ended_candle(self, market: str) -> Candle | None:
        if candles := self._market_candles.get(market):
            return candles[1] if len(candles) > 1 else None

    def subscribe(self, market: str, resolution: str):
        print(f"Subscribing to {resolution} candles for {market}.")
        res = self._map_to_client_resolution(resolution)
        self._ws.candles.subscribe(market, res)

    def unsubscribe(self, market: str, resolution: str) -> None:
        res = self._map_to_client_resolution(resolution)
        self._ws.candles.unsubscribe(market, res)

    def _subscribe_to_all_candles(self):
        for market, res in self._resolutions.items():
            self.subscribe(market, res)

    def _set_subscription_state(self, channel_id: str, state: bool) -> None:
        market = channel_id.split("/")[0]
        self.subscriptions[market] = state

    def handle_message(self, ws: IndexerSocket, message: Dict[str, Any]):
        if message["type"] == "connected":
            self._subscribe_to_all_candles()

        if message["type"] == "subscribed":
            print(f"Subscription successful ({message['channel']}, {message['id']}).")
            self._set_subscription_state(message["id"], True)

        if message["type"] == "unsubscribed":
            print(f"Unsubscription successful ({message['channel']}, {message['id']}).")
            self._set_subscription_state(message["id"], False)

        if message["type"] == "channel_batch_data":
            if candle_dict := message["contents"][0]:
                new_candle = ExchangeCandleMapper.dict_to_candle(
                    self._exchange,
                    candle_dict,
                )
                market = new_candle.market
                active_needs_update = True
                if active_candle := self.get_active_candle(market):
                    if active_candle.started_at < new_candle.started_at:
                        # New candle started
                        self._begin_new_active_candle(market, new_candle)
                        active_needs_update = False

                # Active candle got set or updated
                if active_needs_update:
                    self._update_active_candle(new_candle)

                # DEBUG PRINTS
                if active_candle := self.get_active_candle(market):
                    print(
                        f"Active {market} candle started at: {active_candle.started_at}"
                    )
                if active_candle := self.get_newest_ended_candle(market):
                    print(
                        f"Newest {market } candle started at: {active_candle.started_at}\n"
                    )

    def _begin_new_active_candle(self, market: str, new_candle: Candle) -> None:
        # shift active (at 0) to newest ended (at 1) by inserting the new candle at 0 as new active
        self._market_candles[market].insert(0, new_candle)

    def _update_active_candle(self, new_candle: Candle) -> None:
        if self._market_candles.get(new_candle.market):
            self._market_candles[new_candle.market][0] = new_candle
        else:
            self._market_candles[new_candle.market] = [new_candle]

    def _map_to_client_resolution(
        self,
        dydx_resolution_notation: str,
    ) -> CandlesResolution:
        if key := next(
            (
                key
                for key, value in CandlesResolution.__members__.items()
                if value.value == dydx_resolution_notation
            ),
            None,
        ):
            return CandlesResolution[key]
        else:
            raise ValueError(f"Invalid resolution: {dydx_resolution_notation}.")
