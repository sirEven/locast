from typing import List, Tuple, Type

import pytest


from locast.candle.dydx.dydx_resolution import DydxResolution
from locast.candle.exchange_resolution import (
    ExchangeResolution,
    ResolutionDetail,
    Seconds,
)

# TODO WIP CURRENT: Consider if all functionality tested here is even necessary still.
# TODO: Make Collaboration ready (remove concrete exchange dependencies out of tests, parametrize them)

# TODO: these are actually stupid to maintain... as we don't want to keep updating this list as well... we should
# rather use the concrete implementation (DydxResolution) however: the pros for this list are: we can selectively
# add only those resolutions we want to test (could exclude some, to speed up) and also add faulty ones to test error cases
expected_dydx_resolution_details: List[ResolutionDetail] = [
    ResolutionDetail(Seconds.ONE_DAY, "1DAY"),
    ResolutionDetail(Seconds.FOUR_HOURS, "4HOURS"),
    ResolutionDetail(Seconds.ONE_HOUR, "1HOUR"),
    ResolutionDetail(Seconds.THIRTY_MINUTES, "30MINS"),
    ResolutionDetail(Seconds.FIFTEEN_MINUTES, "15MINS"),
    ResolutionDetail(Seconds.FIVE_MINUTES, "5MINS"),
    ResolutionDetail(Seconds.ONE_MINUTE, "1MIN"),
]

# COLLABORATION: WIP!!! CONTINUE
exchange_resolutions_and_expected_details: List[
    Tuple[
        Type[ExchangeResolution],
        List[ResolutionDetail],
    ],
] = [(DydxResolution, expected_dydx_resolution_details)]


@pytest.mark.parametrize(
    "exchange_resolution",
    exchange_resolutions_and_expected_details,
)
def test_notation_to_resolution_detail_returns_correctly(
    exchange_resolution: Tuple[Type[ExchangeResolution], List[ResolutionDetail]],
) -> None:
    # given
    ex_res = exchange_resolution[0]
    expected_resolution_details: List[ResolutionDetail] = exchange_resolution[1]

    # when & then
    for resolution_detail in expected_resolution_details:
        # when
        result = ex_res.notation_to_resolution_detail(resolution_detail.notation)

        # then
        assert result == resolution_detail
