# Stuff that will be needed down the line:
# - Getting candles via websocket (live) ✅
# - as well as via api requests (historic) ✅
# - sqlite database to store & retrievecandles
# -- build basic infrastructure to fetch historic candles cleanly --
# -- build basic subscribe and unsubscribe from live candle update --

# - For another project:
#   - Opening & closing a position
#   - Querying position data such as pnl...
#   - Querying account balance

import asyncio
import logging
from typing import Any, Dict, List

from dydx_v4_client.indexer.socket.websocket import IndexerSocket, CandlesResolution  # type: ignore
from dydx_v4_client.network import TESTNET  # type: ignore

from locast.candle.candle import Candle
from locast.candle.dydx.dydx_resolution import DydxResolution
from locast.candle.exchange import Exchange
from locast.candle.exchange_candle_mapper import ExchangeCandleMapper

logging.basicConfig(level=logging.DEBUG)


# TODO: implement subscribe and unsubscribe funcs with code from test().
class DydxV4LiveCandle:
    def __init__(
        self,
        resolutions_for_markets: Dict[str, str],
    ) -> None:
        self._exchange = Exchange.DYDX_V4
        self._resolutions = self._convert_to_client_res_dict(resolutions_for_markets)
        self._market_candles: Dict[str, List[Candle]] = {}

    def get_active_candle(self, market: str) -> Candle | None:
        if candles := self._market_candles.get(market):
            return candles[0]

    def get_newest_ended_candle(self, market: str) -> Candle | None:
        if candles := self._market_candles.get(market):
            if len(candles) > 1:
                return candles[1]

    def handle_live_candle_message(self, ws: IndexerSocket, message: Dict[str, Any]):
        if message["type"] == "connected":
            for market, res in self._resolutions.items():
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
        if active_candle := self.get_active_candle("ETH-USD"):
            print(f"Active candle started at: {active_candle.started_at}")
        if active_candle := self.get_newest_ended_candle("ETH-USD"):
            print(f"Newest candle started at: {active_candle.started_at}\n")

    def _begin_new_active_candle(self, market: str, new_candle: Candle) -> None:
        # shift active (at 0) to newest ended (at 1) by inserting the new candle at 0 as new active
        self._market_candles[market].insert(0, new_candle)

    def _update_active_candle(self, new_candle: Candle) -> None:
        if self._market_candles.get(new_candle.market):
            self._market_candles[new_candle.market][0] = new_candle
        else:
            self._market_candles[new_candle.market] = [new_candle]

    def _convert_to_client_res_dict(
        self,
        resolutions_for_markets: Dict[str, str],
    ) -> Dict[str, CandlesResolution]:
        return {
            key: self._map_to_client_resolution(value)
            for key, value in resolutions_for_markets.items()
        }

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


async def test():
    live_candle = DydxV4LiveCandle(
        resolutions_for_markets={
            "ETH-USD": DydxResolution.ONE_MINUTE.notation,
            "BTC-USD": DydxResolution.FIVE_MINUTES.notation,
        },
    )
    await IndexerSocket(
        TESTNET.websocket_indexer,
        on_message=live_candle.handle_live_candle_message,  # type: ignore
    ).connect()


asyncio.run(test())
