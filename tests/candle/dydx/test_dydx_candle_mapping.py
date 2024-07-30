from decimal import Decimal
import pytest
from sir_utilities.date_time import string_to_datetime

from locast.candle.dydx.dydx_candle_mapping import DydxV4CandleMapping
from locast.candle.resolution import Seconds


@pytest.mark.asyncio
async def test_dydx_v4_candle_mapping() -> None:
    # given
    mapping = DydxV4CandleMapping()
    candle_dict = {
        "startedAt": "2024-04-01T09:59:00.000Z",
        "ticker": "ETH-USD",
        "resolution": "1MIN",
        "low": "3537.3",
        "high": "3540.9",
        "open": "3540.9",
        "close": "3537.3",
        "baseTokenVolume": "0.042",
        "usdVolume": "148.6422",
        "trades": 2,
        "startingOpenInterest": "934.027",
    }

    # when
    candle = mapping.dict_to_candle(candle_dict)

    # then
    assert candle.started_at == string_to_datetime("2024-04-01T09:59:00.000Z")
    assert candle.market == "ETH-USD"
    assert candle.resolution == Seconds.ONE_MINUTE
    assert candle.low == Decimal("3537.3")
    assert candle.high == Decimal("3540.9")
    assert candle.open == Decimal("3540.9")
    assert candle.close == Decimal("3537.3")
    assert candle.base_token_volume == Decimal("0.042")
    assert candle.usd_volume == Decimal("148.6422")
    assert candle.trades == 2
    assert candle.starting_open_interest == Decimal("934.027")


@pytest.mark.asyncio
async def test_dydx_v4_candle_mapping_raises_error() -> None:
    # given
    mapping = DydxV4CandleMapping()
    faulty_candle_dict = {
        "startedAt": "2024-04-01T09:59:00.000Z",
        "ticker": "ETH-USD",
        "resolution": "1MIN",
        "low": "3537.3",
    }

    # when & then
    with pytest.raises(ValueError):
        _ = mapping.dict_to_candle(faulty_candle_dict)
