from datetime import datetime
from typing import List


from locast.candle.candle import Candle

from locast.candle.candle_utility import CandleUtility as cu
from locast.candle.exchange import Exchange
from locast.candle.resolution import ResolutionDetail
from locast.candle_fetcher.candle_fetcher import CandleFetcher
from locast.candle_fetcher.dydx.api_fetcher.dydx_v4_fetcher import DydxV4Fetcher


class DydxV4CandleFetcher(CandleFetcher):
    def __init__(self, api_fetcher: DydxV4Fetcher) -> None:
        assertion_error = f"APIFetcher must address API of {Exchange.DYDX_V4.name}."
        assert api_fetcher.exchange == Exchange.DYDX_V4, assertion_error

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
        iteration = 0

        try:
            while (not candles) or candles[-1].started_at > start_date:
                candle_batch: List[Candle] = await self._fetcher.fetch(
                    market,
                    resolution,
                    start_date,
                    temp_end_date,
                )

                candles.extend(candle_batch)
                # TODO: Implement meaningful logging, remove Debug prints
                # print(f"Batch #{iteration} size: {len(candle_batch)}")
                # print(
                #     f"Candles left: {cu.amount_of_candles_in_range(start_date, candles[-1].started_at, resolution)}"
                # )
                temp_end_date = candles[-1].started_at
                iteration += 1
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


class APIException(Exception):
    def __init__(
        self,
        market: str,
        resolution: ResolutionDetail,
        exception: Exception,
        message: str | None = None,
    ) -> None:
        if message is None:
            message = f"Error fetching market data for market '{market}' and resolution '{resolution.notation}: {exception}'."
        super().__init__(message)
