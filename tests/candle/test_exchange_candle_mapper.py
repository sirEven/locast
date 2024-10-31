from typing import Any, Dict, List, Tuple
import pytest

from locast.candle.candle import Candle
from locast.candle.dydx.dydx_candle_mapping import DydxV4CandleMapping
from locast.candle.exchange import Exchange
from locast.candle.exchange_candle_mapper import ExchangeCandleMapper
from locast.candle.exchange_candle_mapping import ExchangeCandleMapping
from tests.helper.candle_mockery.mock_candle import mock_candle
from tests.helper.candle_mockery.dydx_candle_dicts import (
    copy_dydx_v4_base_candle_dict,
)

# COLLABORATION: Testing strategy is to cover concrete implementations such as specific exchange mappers (e.g.: dydx) by parametrizing them into
# the exchange agnostic component tests.
# Here we have examples of this: ExchangeCandleMapper is agnostic and receives a mapping of exchange unspecific ExchangeCandleMapping.
# Through the List on top "mapping_dict_candle" we pair up exchange specific mappings with corresponding candle representation dicts & candles,
# which then are parametrized into the ExchangeCandleMapper component for testing.
# Meaning: Implementing a mapping for another exchange, will only require to expand that list on top by another tuple - assuming the protocol
# structure has been respected (new exchange specific mapping adheres to ExchangeCandleMapping protocol and so on).

mapping_dict_candle: List[Tuple[ExchangeCandleMapping, Dict[str, Any], Candle]] = [
    (
        DydxV4CandleMapping(),
        copy_dydx_v4_base_candle_dict(),
        mock_candle(Exchange.DYDX_V4),
    ),
]


@pytest.mark.parametrize("mapping_dict_candle", mapping_dict_candle)
def test_maps_single_candle_correctly(
    mapping_dict_candle: Tuple[
        ExchangeCandleMapping,
        Dict[str, Any],
        Candle,
    ],
) -> None:
    # given
    mapping = mapping_dict_candle[0]
    candle_dict = mapping_dict_candle[1]
    expected_candle = mapping_dict_candle[2]

    mapper = ExchangeCandleMapper(mapping)

    # when
    candle = mapper.to_candle(candle_dict)

    # then
    assert candle == expected_candle


@pytest.mark.parametrize("mapping_dict_candle", mapping_dict_candle)
def test_mapping_on_faulty_candle_raises_error(
    mapping_dict_candle: Tuple[
        ExchangeCandleMapping,
        Dict[str, Any],
        Candle,
    ],
) -> None:
    # given
    mapping = mapping_dict_candle[0]
    faulty_candle_dict = mapping_dict_candle[1]
    del faulty_candle_dict["startedAt"]
    del faulty_candle_dict["close"]
    mapper = ExchangeCandleMapper(mapping)

    # when & then
    with pytest.raises(ValueError):
        _ = mapper.to_candle(faulty_candle_dict)
