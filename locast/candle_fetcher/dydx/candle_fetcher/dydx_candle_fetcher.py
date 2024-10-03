from datetime import datetime
from typing import List, Tuple


from locast.candle.candle import Candle

from locast.candle.candle_utility import CandleUtility as cu
from locast.candle.exchange import Exchange
from locast.candle.resolution import ResolutionDetail
from locast.candle_fetcher.candle_fetcher import CandleFetcher
from locast.candle_fetcher.dydx.api_fetcher.dydx_fetcher import DydxFetcher
from locast.candle_fetcher.exceptions import APIException
from locast.logging import log_integrity_violations, log_progress


class DydxCandleFetcher(CandleFetcher):
    def __init__(self, api_fetcher: DydxFetcher, log_progress: bool = False) -> None:
        self._log_progress = log_progress
        self._exchange = api_fetcher.exchange
        self._fetcher = api_fetcher

    @property
    def exchange(self) -> Exchange:
        return self._exchange

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
        violations: List[Tuple[Candle, Candle]] = []

        try:
            while (not candles) or candles[-1].started_at > start_date:
                candle_batch: List[Candle] = await self._fetcher.fetch(
                    market,
                    resolution,
                    start_date,
                    temp_end_date,
                )

                if len(candle_batch) > 0:
                    for violation in cu.find_integrity_violations(candle_batch):
                        violations.append(violation)
                        total -= 1

                    if self._log_progress:
                        done += len(candle_batch)
                        log_progress("🚛", "candles", "fetched", done, total)

                    candles.extend(candle_batch)
                    temp_end_date = candles[-1].started_at

                else:
                    break

            if len(violations) > 0:
                log_integrity_violations(
                    "🚨",
                    self._exchange,
                    market,
                    resolution,
                    violations,
                )

        except Exception as e:
            raise APIException(self._exchange, market, resolution, e)

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
