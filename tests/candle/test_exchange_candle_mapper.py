from copy import copy
from decimal import Decimal
from typing import Any, Dict, List, Tuple
import pytest

from sir_utilities.date_time import string_to_datetime
from locast.candle.dydx.dydx_candle_mapping import (
    DydxV3CandleMapping,
    DydxV4CandleMapping,
)
from locast.candle.dydx.dydx_resolution import DydxResolution
from locast.candle.exchange_candle_mapper import ExchangeCandleMapper
from locast.candle.exchange_candle_mapping import ExchangeCandleMapping
from tests.helper.candle_mockery.mock_dydx_candle_dicts import (
    dydx_v3_candle_dict,
    dydx_v4_candle_dict,
)

mappings_and_candle_dicts: List[Tuple[ExchangeCandleMapping, Dict[str, Any]]] = [
    (DydxV4CandleMapping(), dydx_v4_candle_dict),
    (DydxV3CandleMapping(), dydx_v3_candle_dict),
]

# NOTE: Testing strategy is to cover concrete implementations such as specific exchange mappers (e.g.: dydx) by parametrizing them into
# the exchange agnostic component tests.
# Here we have examples of this: ExchangeCandleMapper is agnostic and receives a mapping of exchange nspecific ExchangeCandleMapping.
# Through the List on top "mappings_and_candle_dicts" we team up exchange specific mappings with corresponding candle representation dicts,
# which then are parametrized into the ExchangeCandleMapper component for testing.
# Meaning: Implementing a mapping for another exchange, will only require to expand that list on top by another tuple - assuming the protocol
# structure has been respected (new exchange specific mapping adheres to ExchangeCandleMapping protocol and so on).


# TODO: asserts need to include a universally valid Candle instance, instead of refering back to the exchange specific dict. Why? Because new exchanges will break current test impl.
@pytest.mark.parametrize("mapping_and_dict", mappings_and_candle_dicts)
def test_maps_single_candle_correctly(
    mapping_and_dict: Tuple[ExchangeCandleMapping, Dict[str, Any]],
) -> None:
    # given
    mapping = mapping_and_dict[0]
    candle_dict = mapping_and_dict[1]
    mapper = ExchangeCandleMapper(mapping)

    # when
    candle = mapper.to_candle(candle_dict)

    # then
    assert candle.started_at == string_to_datetime(candle_dict["startedAt"])
    assert (
        candle.market == candle_dict["ticker"]
        if isinstance(mapping, DydxV4CandleMapping)
        else candle_dict["market"]
    )
    assert candle.resolution == DydxResolution.notation_to_seconds(
        candle_dict["resolution"]
    )
    assert candle.low == Decimal(candle_dict["low"])
    assert candle.high == Decimal(candle_dict["high"])
    assert candle.open == Decimal(candle_dict["open"])
    assert candle.close == Decimal(candle_dict["close"])
    assert candle.base_token_volume == Decimal(candle_dict["baseTokenVolume"])
    assert candle.usd_volume == Decimal(candle_dict["usdVolume"])
    assert candle.trades == candle_dict["trades"]
    assert candle.starting_open_interest == Decimal(candle_dict["startingOpenInterest"])


@pytest.mark.parametrize("mapping_and_dict", mappings_and_candle_dicts)
def test_on_faulty_candle_raises_error(
    mapping_and_dict: Tuple[ExchangeCandleMapping, Dict[str, Any]],
) -> None:
    # given
    mapping = mapping_and_dict[0]
    # NOTE: Without copy, this creates corrupting test interference
    faulty_candle_dict = copy(mapping_and_dict[1])
    del faulty_candle_dict["startedAt"]
    del faulty_candle_dict["close"]
    mapper = ExchangeCandleMapper(mapping)

    # when & then
    with pytest.raises(ValueError):
        _ = mapper.to_candle(faulty_candle_dict)
