# Stuff that will be needed down the line:
# - Getting candles via websocket (live) ✅
# - as well as via api requests (historic) ✅
# - Opening & closing a position
# - Querying position data such as pnl...
# - Querying account balance

from datetime import datetime
from typing import List


from locast.candle.candle import Candle
from sir_utilities.date_time import string_to_datetime

from locast.candle.exchange import Exchange
from locast.candle_fetcher.dydx.api_fetcher.dydx_v4_fetcher import DydxV4Fetcher


def candles_left_to_fetch(
    start_date: datetime,
    oldest_fetched_candle: Candle,
) -> int:
    range_seconds = (oldest_fetched_candle.started_at - start_date).total_seconds()
    return int(range_seconds / oldest_fetched_candle.resolution)


# TODO: Implement a check to verify that the newest candle (at 0) has started_at == (utc_now rounded to resolution - 1 resolution)
# If it doesn't, fill the gap. NOTE: This can't be implemented as there is still a bug or restriction in the testnet backend, preventing historic
# candle fetches up to present candle. - BUT we can do it now with mocked candles.


class DydxCandleFetcher:
    def __init__(self, dydx_v4_fetcher: DydxV4Fetcher | None = DydxV4Fetcher()) -> None:
        if dydx_v4_fetcher:
            self._fetchers = {Exchange.DYDX_V4: dydx_v4_fetcher}

    def datetime_to_dydx_iso_str(self, date: datetime) -> str:
        return date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    async def fetch_candles(
        self,
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

        if not (fetcher := self._fetchers.get(exchange)):
            raise ValueError(
                f"Candlefetcher can't be selected for unknown exchange: {exchange}."
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
                # DEBUG prints
                print(f"Batch #{count} size: {len(candle_batch)}")
                print(
                    f"Candles left to download: {candles_left_to_fetch(start_date_dt, candles[-1])}"
                )
                temp_end_date = self.datetime_to_dydx_iso_str(candles[-1].started_at)
                count += 1
        except Exception as e:
            print(e)

        return candles

    # WIP: Implement and test against new mocked component
    async def fetch_cluster(
        self,
        exchange: Exchange,
        market: str,
        resolution: str,
        start_date: str,
    ) -> List[Candle]:
        """
        Fetches a cluster of candles, which is a group of chronologically sorted, uninterrupted candles ranging
        from a given start date up to the most recently finished candle.
        """
        candles: List[Candle] = []

        # while loop:
        # now = DydxCandleFetcher.datetime_to_dydx_iso_str(datetime.now(timezone.utc)) TODO: Rounded to minutes
        # while (not candles) or candles[0].started_at < now:
        # fetch_historic_candles(dydx, eth, 1min, temp_start_date, now)

    async def update_cluster(self, cluster_head: Candle) -> List[Candle]:
        """
        Updates the cluster by adding new candles based on the provided cluster_head.

        Parameters:
            cluster_head (Candle): The head of the cluster to be updated.

        Returns:
            List[Candle]: The updated list of candles in the cluster.
        """

        pass
