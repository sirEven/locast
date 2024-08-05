# Stuff that will be needed down the line:
# - Getting candles via websocket (live) ✅
# - as well as via api requests (historic) ✅
# - sqlite database to store & retrieve candles
# -- build basic infrastructure to fetch historic candles cleanly --

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
from locast.live_candle.live_candle import LiveCandle

logging.basicConfig(level=logging.DEBUG)


# TODO: Pull in event_systems and publish finished candles
class DydxV4LiveCandle(LiveCandle):
    def __init__(
        self,
        host_url: str,
        resolutions_for_markets: Dict[
            str, str
        ],  # TODO: Change to [str, List[str]]->{resolution: [markets]}
    ) -> None:
        self._ws = IndexerSocket(host_url, on_message=self.handle_message)  # type: ignore
        self._exchange = Exchange.DYDX_V4
        self._resolutions = resolutions_for_markets
        self._market_candles: Dict[str, List[Candle]] = {}
        self.subscriptions: Dict[str, bool] = {}

    def _wrap_async_func(self) -> None:
        # self._ws.connect() is a blocking async function call that needs to be wrapped
        asyncio.run(self._ws.connect())  # type: ignore

    def start(self) -> None:
        t = threading.Thread(target=self._wrap_async_func)
        t.start()

    def stop(self) -> None:
        self._unsubscribe_from_all_candles()
        self._ws.close()  # type: ignore

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
        print(f"Unsubscribing from {resolution} candles for {market}.")
        res = self._map_to_client_resolution(resolution)
        self._ws.candles.unsubscribe(market, res)

    def _subscribe_to_all_candles(self) -> None:
        for market, res in self._resolutions.items():
            self.subscribe(market, res)

    def _unsubscribe_from_all_candles(self) -> None:
        for market, res in self._resolutions.items():
            self.unsubscribe(market, res)

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
