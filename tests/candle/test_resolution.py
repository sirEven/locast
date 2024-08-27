import pytest
from typing import List, Tuple

from locast.candle.dydx.dydx_resolution import DydxResolution
from locast.candle.resolution import ExchangeResolution, ResolutionDetail, Seconds

dydx_resolution_details: List[ResolutionDetail] = [
    ResolutionDetail(Seconds.ONE_DAY, "1DAY"),
    ResolutionDetail(Seconds.FOUR_HOURS, "4HOURS"),
    ResolutionDetail(Seconds.ONE_HOUR, "1HOUR"),
    ResolutionDetail(Seconds.THIRTY_MINUTES, "30MINS"),
    ResolutionDetail(Seconds.FIFTEEN_MINUTES, "15MINS"),
    ResolutionDetail(Seconds.FIVE_MINUTES, "5MINS"),
    ResolutionDetail(Seconds.ONE_MINUTE, "1MIN"),
]

dydx_faulty_resolution_detail: ResolutionDetail = ResolutionDetail(
    Seconds.ONE_WEEK,
    "INVALID_NOTATION",
)


@pytest.mark.parametrize(
    "exchange_resolution",
    [(DydxResolution, dydx_resolution_details)],
)
def test_notation_to_seconds_returns_correctly(
    exchange_resolution: Tuple[ExchangeResolution, List[ResolutionDetail]],
) -> None:
    # given
    exchange_res = exchange_resolution[0]
    resolution_details = exchange_resolution[1]

    # when & then
    for resolution_detail in resolution_details:
        # when
        result_sec = exchange_res.notation_to_seconds(resolution_detail.notation)

        # then
        assert result_sec == resolution_detail.seconds


@pytest.mark.parametrize(
    "exchange_resolution",
    [(DydxResolution, dydx_resolution_details)],
)
def test_seconds_to_notation_returns_correctly(
    exchange_resolution: Tuple[ExchangeResolution, List[ResolutionDetail]],
) -> None:
    # given
    exchange_res = exchange_resolution[0]
    resolution_details = exchange_resolution[1]

    # when & then
    for resolution_detail in resolution_details:
        # when
        result_notation = exchange_res.seconds_to_notation(resolution_detail.seconds)

        # then
        assert result_notation == resolution_detail.notation


@pytest.mark.parametrize(
    "exchange_resolution",
    [(DydxResolution, dydx_faulty_resolution_detail)],
)
def test_notation_to_seconds_raises_error(
    exchange_resolution: Tuple[ExchangeResolution, ResolutionDetail],
) -> None:
    # given
    exchange_res = exchange_resolution[0]
    faulty_resolution_detail = exchange_resolution[1]

    # when & then
    with pytest.raises(ValueError):
        exchange_res.notation_to_seconds(faulty_resolution_detail.notation)


@pytest.mark.parametrize(
    "exchange_resolution",
    [(DydxResolution, dydx_faulty_resolution_detail)],
)
def test_seconds_to_notation_raises_error(
    exchange_resolution: Tuple[ExchangeResolution, ResolutionDetail],
) -> None:
    # given
    exchange_res = exchange_resolution[0]
    faulty_resolution_detail = exchange_resolution[1]

    # when & then
    with pytest.raises(ValueError):
        exchange_res.seconds_to_notation(faulty_resolution_detail.seconds)
