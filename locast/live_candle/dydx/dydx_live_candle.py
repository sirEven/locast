# Stuff that will be needed down the line:
# - Getting candles via websocket (live) ✅
# - as well as via api requests (historic) ✅
# - sqlite database to store & retrieve candles ✅
# -- build basic infrastructure to fetch historic candles cleanly -- ✅

# - For another project:
#   - Opening & closing a position
#   - Querying position data such as pnl...
#   - Querying account balance

import asyncio
import threading
from typing import Any, Dict, List

from dydx_v4_client.indexer.socket.websocket import (  # type: ignore
    CandlesResolution,
    IndexerSocket,
)

from locast.candle.candle import Candle
from locast.candle.dydx.dydx_candle_mapping import DydxV4CandleMapping
from locast.candle.exchange_candle_mapper import ExchangeCandleMapper
from locast.live_candle.live_candle import LiveCandle

# logging.basicConfig(level=logging.DEBUG)


# NOTE: This is an experimental component, not yet in use.
class DydxV4LiveCandle(LiveCandle):
    def __init__(
        self,
        host_url: str,
        markets_per_resolution: Dict[str, List[str]],
    ) -> None:
        self._connection_id: str | None = None
        self._ws = IndexerSocket(host_url, on_message=self.handle_message)  # type: ignore
        self._mapper = ExchangeCandleMapper(DydxV4CandleMapping())
        self._markets_per_resolution = markets_per_resolution
        self._market_candles: Dict[str, List[Candle]] = {}
        self.subscriptions: Dict[str, bool] = {}

    async def start(self) -> None:
        print("Starting live candle.")
        t = threading.Thread(target=self._wrap_async_func, name="live_candle")
        t.start()

        while not self._connection_id:
            await asyncio.sleep(0)

        await self._subscribe_to_all_candles()

        while not self.all_are_live():
            await asyncio.sleep(0)

    async def stop(self) -> None:
        print("Stopping live candle.")
        await self._unsubscribe_from_all_candles()
        while self.some_are_live():
            await asyncio.sleep(0)
        self._ws.close()  # type: ignore
        self._connection_id = None

    def get_active_candle(self, market: str) -> Candle | None:
        if candles := self._market_candles.get(market):
            return candles[0]

    def get_newest_ended_candle(self, market: str) -> Candle | None:
        if candles := self._market_candles.get(market):
            return candles[1] if len(candles) > 1 else None

    async def subscribe(self, market: str, resolution: str):
        print(f"Subscribing to {resolution} candles for {market}.")
        res = self._map_to_client_resolution(resolution)
        self._ws.candles.subscribe(market, res)
        while not self.subscriptions.get(market):
            await asyncio.sleep(0)

    async def unsubscribe(self, market: str, resolution: str) -> None:
        print(f"Unsubscribing from {resolution} candles for {market}.")
        res = self._map_to_client_resolution(resolution)
        self._ws.candles.unsubscribe(market, res)
        while self.subscriptions.get(market):
            await asyncio.sleep(0)

    def all_are_live(self) -> bool:
        return bool(self.subscriptions) and all(
            self.subscriptions.get(market) for market in self.subscriptions
        )

    def some_are_live(self) -> bool:
        return any(
            self.subscriptions.get(market) for market in list(self.subscriptions.keys())
        )

    def handle_message(self, ws: IndexerSocket, message: Dict[str, Any]):
        if message["type"] == "connected":
            connection_id = message["connection_id"]
            self._connection_id = connection_id
            print(f"Connection successful (id: {connection_id}).")

        if message["type"] == "subscribed":
            print(f"Subscription successful ({message['channel']}, {message['id']}).")
            self._set_subscription_state(message["id"], True)

        if message["type"] == "unsubscribed":
            print(f"Unsubscription successful ({message['channel']}, {message['id']}).")
            self._set_subscription_state(message["id"], False)

        if message["type"] == "channel_batch_data":
            if candle_dict := message["contents"][0]:
                new_candle = self._mapper.to_candle(
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

    def _wrap_async_func(self) -> None:
        # self._ws.connect() is a blocking async function call that needs to be wrapped
        asyncio.run(self._ws.connect())  # type: ignore

    async def _subscribe_to_all_candles(self) -> None:
        for res, markets in self._markets_per_resolution.items():
            for market in markets:
                await self.subscribe(market, res)

    async def _unsubscribe_from_all_candles(self) -> None:
        for res, markets in self._markets_per_resolution.items():
            for market in markets:
                await self.unsubscribe(market, res)

    def _set_subscription_state(self, channel_id: str, state: bool) -> None:
        market = channel_id.split("/")[0]
        self.subscriptions[market] = state

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
