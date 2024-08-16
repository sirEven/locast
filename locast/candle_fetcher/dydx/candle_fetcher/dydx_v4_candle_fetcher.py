# Stuff that will be needed down the line:
# - Getting candles via websocket (live) ✅
# - as well as via api requests (historic) ✅
# - Opening & closing a position
# - Querying position data such as pnl...
# - Querying account balance

from datetime import datetime
from typing import List


from locast.candle.candle import Candle

from locast.candle.candle_utility import CandleUtility as cu
from locast.candle.dydx.dydx_resolution import DydxResolution
from locast.candle_fetcher.api_fetcher import APIFetcher
from locast.candle_fetcher.candle_fetcher import CandleFetcher


class DydxV4CandleFetcher(CandleFetcher):
    def __init__(self, api_fetcher: APIFetcher) -> None:
        self._fetcher = api_fetcher

    async def fetch_candles(
        self,
        market: str,
        resolution: str,
        start_date: datetime,
        end_date: datetime,
    ) -> List[Candle]:
        """
        Fetches candles from the specified exchange and market within a given time range.

        Args:
            exchange (Exchange): The exchange to fetch candles from.
            market (str): The market to fetch candles for.
            resolution (str): The resolution of the candles to fetch.
            start_date (datetime): The start date of the time range (the started_at value of the oldest candle in the range).
            end_date (datetime): The end date of the time range (the theoretical end date of the newest candle in the range).

        Returns:
            List[Candle]: A list of candles fetched from the specified exchange and market.

        Note: This function does not guarantee its returned candles to be reaching to the most recent existing candle on the exchange.
        It simply fetches candles making up the range between the provided start_date and end_date. If this takes longer than newer
        candles to be created on the exchange, those candles will not be fetched.
        """
        candles: List[Candle] = []

        temp_end_date = end_date
        count = 0

        try:
            while (not candles) or candles[-1].started_at > start_date:
                candle_batch: List[Candle] = await self._fetcher.fetch(
                    market,
                    resolution,
                    start_date,
                    temp_end_date,
                )

                candles.extend(candle_batch)
                # DEBUG prints
                print(f"Batch #{count} size: {len(candle_batch)}")
                print(
                    f"Candles left: {cu.amount_of_candles_in_range(start_date, candles[-1].started_at, candles[-1].resolution)}"
                )
                temp_end_date = candles[-1].started_at
                count += 1
        except Exception as e:
            print(e)

        return candles

    async def fetch_candles_up_to_now(
        self,
        market: str,
        resolution: str,
        start_date: datetime,
    ) -> List[Candle]:
        """
        Fetches a cluster of candles, which is a group of chronologically sorted, uninterrupted candles ranging
        from a given start date up to the most recently finished candle.

        Args:
            exchange (Exchange): The exchange to fetch candles from.
            market (str): The market to fetch candles for.
            resolution (str): The resolution of the candles to fetch.
            start_date (datetime): The start date of the time range (the started_at value of the oldest candle in the range).

        Returns:
            List[Candle]: A list of candles from the start date up to the most recently finished candle.
        """
        candles: List[Candle] = []
        res_sec = DydxResolution.notation_to_seconds(resolution)

        temp_start_date = start_date
        temp_norm_now = cu.normalized_now(res_sec)

        # This is what we wait for: The newest candle (at index 0) to have started_at one resolution below NOW,
        # which only happens, if during fetch_candles a new candle started.
        temp_now_minus_res = cu.subtract_one_resolution(temp_norm_now, res_sec)
        while (not candles) or candles[0].started_at < temp_now_minus_res:
            new_candles = await self.fetch_candles(
                market,
                resolution,
                temp_start_date,
                temp_norm_now,
            )

            # Sort repeated fetches to the front of gathered candles
            if new_candles:
                candles = new_candles + candles

            # Update input for next iteration
            next_started_at = cu.add_one_resolution(candles[0].started_at, res_sec)

            temp_start_date = next_started_at
            temp_norm_now = cu.normalized_now(res_sec)
            temp_now_minus_res = cu.subtract_one_resolution(temp_norm_now, res_sec)

        return candles

    # TODO: This is actually a higher level (Controller) method, together with create_cluster().
    async def update_cluster(self, cluster_head: Candle) -> List[Candle]:
        """
        Updates the cluster by adding new candles based on the provided cluster_head.

        Parameters:
            cluster_head (Candle): The head of the cluster to be updated. This is the
            candle with the most recent started_at date in the cluster.

        Returns:
            List[Candle]: The candles needed to update the cluster to include the most
            recent price data.
        """

        raise NotImplementedError
