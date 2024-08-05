import asyncio
from typing import List
from locast.live_candle.dydx.dydx_live_candle import DydxV4LiveCandle
from dydx_v4_client.network import TESTNET  # type: ignore
from locast.candle.dydx.dydx_resolution import DydxResolution


live_candle = DydxV4LiveCandle(
    host_url=TESTNET.websocket_indexer,
    resolutions_for_markets={
        "ETH-USD": DydxResolution.ONE_MINUTE.notation,
        "BTC-USD": DydxResolution.ONE_MINUTE.notation,
    },
)


# This simulates a different component trying to query the live candle for data
async def price_query(live_candle: DydxV4LiveCandle, markets: List[str]) -> None:
    print("debug, entering price_query!")
    while True:
        for market in markets:
            if live_candle.subscriptions.get(market):
                if candle := live_candle.get_newest_ended_candle(market):
                    print(f"{market} CLOSE: {candle.close}")

        await asyncio.sleep(5)


async def unsubscribe_after_delay(
    live_candle: DydxV4LiveCandle,
    market: str,
    delay_sec: int,
) -> None:
    await asyncio.sleep(delay_sec)
    print(f"Unsubscribing from {market}.")
    live_candle.unsubscribe(market, DydxResolution.ONE_MINUTE.notation)


async def subscribe_after_delay(
    live_candle: DydxV4LiveCandle, market: str, delay_sec: int
) -> None:
    await asyncio.sleep(delay_sec)
    print(f"Subscribing to {market}.")
    live_candle.subscribe(market, DydxResolution.ONE_MINUTE.notation)


async def main():
    live_candle.start()
    tasks = [
        asyncio.create_task(price_query(live_candle, ["ETH-USD", "BTC-USD"])),
        asyncio.create_task(unsubscribe_after_delay(live_candle, "ETH-USD", 80)),
        asyncio.create_task(subscribe_after_delay(live_candle, "ETH-USD", 140)),
    ]
    await asyncio.gather(*tasks)


asyncio.run(main())
