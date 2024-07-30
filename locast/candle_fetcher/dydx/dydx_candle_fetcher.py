# Stuff that will be needed down the line:
# - Getting candles via websocket (live) ✅
# - as well as via api requests (historic) ✅
# - Opening & closing a position
# - Querying position data such as pnl...
# - Querying account balance

from datetime import datetime
from typing import Any, Dict, List

from dydx_v4_client.indexer.rest.indexer_client import IndexerClient  # type: ignore
from dydx_v4_client.network import TESTNET  # type: ignore


from locast.candle.candle import Candle
from sir_utilities.date_time import string_to_datetime

from locast.candle.exchange import Exchange
from locast.candle.exchange_candle_mapper import ExchangeCandleMapper


def candles_left_to_fetch(
    start_date: datetime,
    oldest_fetched_candle: Candle,
) -> int:
    range_seconds = (oldest_fetched_candle.started_at - start_date).total_seconds()
    return int(range_seconds / oldest_fetched_candle.resolution)


# TODO: Implement a check to verify that the newest candle (at 0) has started_at == utc_now (rounded to resolution)
# If it doesn't, fill the gap. NOTE: This can't be implemeented as there is still a bug in the client, preventing historic
# candle fetches up to present candle.
class DydxV4Fetcher:
    client = IndexerClient(TESTNET.rest_indexer)

    async def fetch(
        self,
        market: str,
        resolution: str,
        start_date: str,
        end_date: str,
    ) -> List[Candle]:
        response: Dict[
            str, Any
        ] = await self.client.markets.get_perpetual_market_candles(  # type: ignore
            market=market,
            resolution=resolution,
            from_iso=start_date,
            to_iso=end_date,
        )
        assert response["candles"]
        return ExchangeCandleMapper.dicts_to_candles(
            Exchange.DYDX_V4,
            response["candles"],
        )


class DydxV3Fetcher:
    pass


class DydxCandleFetcher:
    @staticmethod
    def datetime_to_dydx_iso_str(date: datetime) -> str:
        return date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    fetchers = {Exchange.DYDX_V4: DydxV4Fetcher()}

    @staticmethod
    async def fetch_historic_candles(
        exchange: Exchange,
        market: str,
        resolution: str,
        start_date: str,
        end_date: str,
    ) -> List[Candle]:
        candles: List[Candle] = []

        start_date_dt = string_to_datetime(start_date)
        temp_end_date = end_date
        count = 0

        if not (fetcher := DydxCandleFetcher.fetchers.get(exchange)):
            raise ValueError(
                f"Fetcher can't be selected for unknown exchange: {exchange}."
            )

        try:
            while (not candles) or candles[-1].started_at > start_date_dt:
                candle_batch: List[Candle] = await fetcher.fetch(
                    market,
                    resolution,
                    start_date,
                    temp_end_date,
                )

                candles.extend(candle_batch)
                print(f"Batch #{count} size: {len(candle_batch)}")
                print(
                    f"Candles left to download: {candles_left_to_fetch(start_date_dt, candles[-1])}"
                )
                temp_end_date = DydxCandleFetcher.datetime_to_dydx_iso_str(
                    candles[-1].started_at
                )
                count += 1
        except Exception as e:
            print(e)

        return candles


# async def test():
#     candles = await DydxCandleFetcher.fetch_historic_candles(
#         Exchange.DYDX_V4,
#         LINK_USD,
#         DydxResolution.ONE_MINUTE.notation,
#         "2024-05-01T00:00:00.000Z",
#         DydxCandleFetcher.datetime_to_dydx_iso_str(datetime.now(timezone.utc)),
#     )
#     print(f"{len(candles)} candles")
#     print(f"Oldest candle started at: {candles[-1].started_at}")
#     print(f"Newest candle started at: {candles[0].started_at}")


# asyncio.run(test())
