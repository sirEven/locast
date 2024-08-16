from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sir_utilities.date_time import datetime_to_string, string_to_datetime

from locast.candle.candle_utility import CandleUtility as cu
from dydx_v4_client.indexer.rest.indexer_client import IndexerClient, MarketsClient  # type: ignore
from dydx_v4_client.network import TESTNET  # type: ignore

from locast.candle.dydx.dydx_resolution import DydxResolution


class V4MarketsClientMock(MarketsClient):
    def __init__(self) -> None:
        self._mock_candle_base: Dict[str, Any] = {
            "startedAt": "2024-05-06T17:24:00.000Z",
            "ticker": "LINK-USD",
            "resolution": "1MIN",
            "low": "14.688",
            "high": "14.688",
            "open": "14.688",
            "close": "14.688",
            "baseTokenVolume": "0",
            "usdVolume": "0",
            "trades": 0,
            "startingOpenInterest": "11132",
        }

        self._temp_candle = self._mock_candle_base

    async def get_perpetual_market_candles(
        self,
        market: str,
        resolution: str,
        from_iso: Optional[str] = None,
        to_iso: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Generates mocked price candles for a given market, resolution, and time range.

        Args:
            market (str): The market for which to retrieve candles.
            resolution (str): The resolution of the candles.
            from_iso (Optional[str], optional): The start date of the candle range in ISO format. Defaults to None.
            to_iso (Optional[str], optional): The end date of the candle range in ISO format. Defaults to None.
            limit (Optional[int], optional): The maximum number of candles to retrieve. Defaults to None.

        Returns:
            Dict[str, Any]: A dictionary containing a list of candle dictionaries.

        Raises:
            AssertionError: If to_iso or from_iso is not provided when mocking candles.

        Note:
            1) Before the first iteration we always add the first candle to the (then empty) batch in order to
            simplify the index based algorithm and prevent duplicates (at the end of one batch and the beginning of the next).
            While doing so we also modify certain attributes of that first batch candle, to correspond to the input resolution
            and date range.
            2) Specifically we subtract one resolution from the date, because the very first candle (which is the most
            recent one chronologically aka the newest one) will only reach to the to_iso date from its startedAt date which
            is one resolution earlier.
            3) Because of this strategy (adding the first candle by hand) we need to subtract 1 from the range input in our
            for loop, since we want every batch to be either 1000 candles (batch size by which mainnet backend responds) wide
            or less, if the provided range entails less.

        """
        assert to_iso, "to_iso must be provided when mocking candles."
        assert from_iso, "from_iso must be provided when mocking candles."

        batch_size = 1000

        self._temp_candle = self._replace_date(
            self._temp_candle,
            self._subtract_resolution(to_iso, resolution),
        )

        self._temp_candle["resolution"] = resolution
        candle_dicts_batch: List[Dict[str, Any]] = [self._temp_candle]

        amount = min(
            cu.amount_of_candles_in_range(
                string_to_datetime(from_iso),
                string_to_datetime(to_iso),
                DydxResolution.notation_to_seconds(resolution),
            ),
            batch_size,
        )
        for i in range(amount - 1):
            new_date = self._subtract_resolution(
                candle_dicts_batch[i]["startedAt"],
                candle_dicts_batch[i]["resolution"],
            )
            candle_dict = self._replace_date(candle_dicts_batch[i].copy(), new_date)
            candle_dicts_batch.append(candle_dict)

        return {"candles": candle_dicts_batch}

    def _replace_date(
        self,
        candle_dict: Dict[str, Any],
        date: datetime,
    ) -> Dict[str, Any]:
        date_rounded = date.replace(microsecond=0, second=0)
        candle_dict["startedAt"] = datetime_to_string(date_rounded)
        return candle_dict

    def _subtract_resolution(self, date_str: str, resolution: str) -> datetime:
        date = string_to_datetime(date_str)
        res_sec = DydxResolution.notation_to_seconds(resolution)
        return date - timedelta(seconds=res_sec)


class V4IndexerClientMock(IndexerClient):
    def __init__(self, host: str = TESTNET.rest_indexer) -> None:
        super().__init__(host=host)
        self._markets = V4MarketsClientMock()

    @property
    def markets(self) -> MarketsClient:
        return self._markets
