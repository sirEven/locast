import asyncio
from typing import List
from locast.live_candle.dydx.dydx_live_candle import DydxV4LiveCandle
from dydx_v4_client.network import TESTNET  # type: ignore
from locast.candle.dydx.dydx_resolution import DydxResolution


# This simulates a different component trying to query the live candle for data
async def price_query(live_candle: DydxV4LiveCandle, markets: List[str]) -> None:
    print("debug, entering price_query!")
    while live_candle.some_are_live():
        for market in markets:
            if live_candle.subscriptions.get(market) is True:
                if candle := live_candle.get_newest_ended_candle(market):
                    print(f"{market} CLOSE: {candle.close}")

        await asyncio.sleep(5)


async def unsubscribe_after_delay(
    live_candle: DydxV4LiveCandle,
    market: str,
    delay_sec: int,
) -> None:
    await asyncio.sleep(delay_sec)
    await live_candle.unsubscribe(market, DydxResolution.ONE_MINUTE.notation)


async def subscribe_after_delay(
    live_candle: DydxV4LiveCandle, market: str, delay_sec: int
) -> None:
    await asyncio.sleep(delay_sec)
    await live_candle.subscribe(market, DydxResolution.ONE_MINUTE.notation)


async def stop_after_delay(live_candle: DydxV4LiveCandle, delay_sec: int) -> None:
    await asyncio.sleep(delay_sec)
    await live_candle.stop()


async def main():
    live_candle = DydxV4LiveCandle(
        host_url=TESTNET.websocket_indexer,
        markets_per_resolution={
            DydxResolution.ONE_MINUTE.notation: ["ETH-USD", "BTC-USD"],
        },
    )

    await live_candle.start()
    tasks = [
        asyncio.create_task(price_query(live_candle, ["ETH-USD", "BTC-USD"])),
        asyncio.create_task(unsubscribe_after_delay(live_candle, "ETH-USD", 80)),
        asyncio.create_task(subscribe_after_delay(live_candle, "ETH-USD", 140)),
        asyncio.create_task(stop_after_delay(live_candle, 200)),
    ]
    await asyncio.gather(*tasks)


asyncio.run(main())
