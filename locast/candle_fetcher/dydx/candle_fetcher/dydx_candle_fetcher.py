from datetime import datetime
from typing import List


from locast.candle.candle import Candle

from locast.candle.candle_utility import CandleUtility as cu
from locast.candle.exchange import Exchange
from locast.candle.exchange_resolution import ResolutionDetail
from locast.candle_fetcher.candle_fetcher import CandleFetcher
from locast.candle_fetcher.dydx.api_fetcher.dydx_fetcher import DydxFetcher
from locast.candle_fetcher.exceptions import APIException
from locast.logging_functions import log_missing_candles, log_progress


class DydxCandleFetcher(CandleFetcher):
    def __init__(self, api_fetcher: DydxFetcher, log_progress: bool = False) -> None:
        self._log_progress = log_progress
        self._exchange = api_fetcher.exchange
        self._fetcher = api_fetcher

    @property
    def exchange(self) -> Exchange:
        return self._exchange

    @property
    def log_progress(self) -> bool:
        return self._log_progress

    @log_progress.setter
    def log_progress(self, value: bool) -> None:
        self._log_progress = value

    async def fetch_candles(
        self,
        market: str,
        resolution: ResolutionDetail,
        start_date: datetime,
        end_date: datetime,
    ) -> List[Candle]:
        """
        Fetches candles from exchange (derived from api_fetcher) and market within a given time range.

        Args:
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
        total = cu.amount_of_candles_in_range(start_date, end_date, resolution)
        done = 0
        total_missing_candles: List[datetime] = []

        try:
            while (not candles) or candles[-1].started_at > start_date:
                candle_batch: List[Candle] = await self._fetcher.fetch(
                    market,
                    resolution,
                    start_date,
                    temp_end_date,
                )

                if not candle_batch:
                    break

                prev_oldest_date = candles[-1].started_at if candles else end_date

                if missing_in_batch := self._detect_missing_in_batch(
                    candle_batch,
                    prev_oldest_date,
                ):
                    total -= len(missing_in_batch)
                    total_missing_candles.extend(missing_in_batch)

                if self._log_progress:
                    done += len(candle_batch)
                    log_progress("🚛", "candles", "fetched", done, total)

                candles.extend(candle_batch)
                temp_end_date = candles[-1].started_at

            # TODO: See if ordering total_missing_candles might make sense.
            if total_missing_candles:
                log_missing_candles(
                    "🚨",
                    self._exchange,
                    market,
                    resolution,
                    total_missing_candles,
                )

        except Exception as e:
            raise APIException(self._exchange, market, resolution, e) from e

        return candles

    async def fetch_candles_up_to_now(
        self,
        market: str,
        resolution: ResolutionDetail,
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

        temp_start_date = start_date
        temp_norm_now = cu.normalized_now(resolution)

        # This is what we wait for: The newest candle (at index 0) to have started_at one resolution below NOW,
        # which only happens, if during fetch_candles a new candle started.
        temp_now_minus_res = cu.subtract_n_resolutions(temp_norm_now, resolution, 1)
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
            next_started_at = cu.add_one_resolution(candles[0].started_at, resolution)

            temp_start_date = next_started_at
            temp_norm_now = cu.normalized_now(resolution)
            temp_now_minus_res = cu.subtract_n_resolutions(temp_norm_now, resolution, 1)

        return candles

    # TODO: Missing candles can eff this up - but chances are tiny...
    async def find_horizon(self, market: str, resolution: ResolutionDetail) -> datetime:
        now = cu.normalized_now(resolution)
        step = 1000  # TODO: Optimize this value (depending on resolution)
        upper_bound = now
        lower_bound = None

        # Step 1: Exponential Back-Off Search
        while True:
            back_n = cu.subtract_n_resolutions(now, resolution, step)
            back_n_plus_resolution = cu.add_one_resolution(back_n, resolution)

            # Query the single candle over the range [back_n, back_n + resolution]
            candle = await self._fetcher.fetch(
                market,
                resolution,
                back_n,
                back_n_plus_resolution,
            )
            # print(f"back_n: {back_n}")
            # Candle exists, continue back-off
            if candle:
                upper_bound = back_n  # Move the upper bound further back
                step *= 2  # Double the step size
            else:
                lower_bound = back_n  # We've gone too far, set this as the lower bound
                break

        # Step 2: Binary Search within the determined range
        delta = upper_bound - lower_bound

        while delta.total_seconds() > resolution.seconds:
            mid_point = cu.norm_date(cu.midpoint(lower_bound, upper_bound), resolution)
            mid_point_plus_resolution = cu.add_one_resolution(mid_point, resolution)

            # Query for a single candle covering [mid_point, mid_point + resolution]
            candle = await self._fetcher.fetch(
                market, resolution, mid_point, mid_point_plus_resolution
            )
            # print(f"delta: {delta}")
            # print(f"upper_bound: {upper_bound}")
            # print(f"lower_bound: {lower_bound}")
            if candle:
                # Move the upper bound down (closer to the lower bound)
                upper_bound = mid_point
            else:
                # Move the lower bound up (closer to the upper bound)
                lower_bound = mid_point

            delta = upper_bound - lower_bound
        # Step 3: Final Candle Fetch to Confirm the Oldest Available Candle
        upper_bound_plus_resolution = cu.add_one_resolution(upper_bound, resolution)
        final_candle = await self._fetcher.fetch(
            market, resolution, upper_bound, upper_bound_plus_resolution
        )

        return final_candle[0].started_at

    def _detect_missing_in_batch(
        self,
        candle_batch: List[Candle],
        previous_last_candle: datetime,
    ) -> List[datetime]:
        dates_to_check = [candle.started_at for candle in candle_batch]

        # Insert last candle of previous batch to have overlap to cover candles missing in between batches
        dates_to_check.insert(0, previous_last_candle)

        return cu.detect_missing_dates(dates_to_check, candle_batch[0].resolution)
