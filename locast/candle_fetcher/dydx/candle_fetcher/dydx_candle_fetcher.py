from datetime import datetime
from typing import List


from locast.candle.candle import Candle

from locast.candle.candle_utility import CandleUtility as cu
from locast.candle.exchange import Exchange
from locast.candle.resolution import ResolutionDetail
from locast.candle_fetcher.api_exception import APIException
from locast.candle_fetcher.candle_fetcher import CandleFetcher
from locast.candle_fetcher.dydx.api_fetcher.dydx_fetcher import DydxFetcher
from locast.logging import log_progress


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
        iteration = 0

        total, done = self._create_log_vars(resolution, start_date, end_date)

        try:
            while (not candles) or candles[-1].started_at > start_date:
                candle_batch: List[Candle] = await self._fetcher.fetch(
                    market,
                    resolution,
                    start_date,
                    temp_end_date,
                )

                candles.extend(candle_batch)
                temp_end_date = candles[-1].started_at
                iteration += 1

                if self._log_progress:
                    done += len(candle_batch)
                    log_progress("🚛", "candles", "fetched", done, total)

        except Exception as e:
            raise APIException(market, resolution, e) from e

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

    def _create_log_vars(
        self,
        resolution: ResolutionDetail,
        start_date: datetime,
        end_date: datetime,
    ):
        if self._log_progress:
            total = cu.amount_of_candles_in_range(start_date, end_date, resolution)
            done = 0
        else:
            done = 0
            total = 0
        return total, done
