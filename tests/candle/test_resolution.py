from typing import List, Type

import pytest


from locast.candle.dydx.dydx_resolution import DydxResolution
from locast.candle.exchange_resolution import (
    ExchangeResolution,
    ResolutionDetail,
)


# COLLABORATION: Add additional exchange specific resolutions to the list
exchange_resolutions: List[Type[ExchangeResolution]] = [DydxResolution]


@pytest.mark.parametrize("exchange_resolution", exchange_resolutions)
def test_notation_to_resolution_detail_returns_correctly(
    exchange_resolution: ExchangeResolution,
) -> None:
    # given

    notations = _get_notations(exchange_resolution)
    # when & then
    for expected_notation in notations:
        # when
        detail = exchange_resolution.notation_to_resolution_detail(expected_notation)

        # then
        assert detail.notation == expected_notation


def _get_notations(cls: ExchangeResolution) -> List[str]:
    return [
        getattr(cls, attr).notation
        for attr in dir(cls)
        if isinstance(getattr(cls, attr), ResolutionDetail)
    ]
