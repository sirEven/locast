from dataclasses import dataclass
from typing import Any
from dydx3 import Client  # type: ignore
from dydx3.modules.public import Public  # type: ignore
from dydx3.helpers.requests import Response  # type: ignore

from locast.candle.exchange import Exchange
from tests.helper.candle_mockery.dydx_candle_backend_mock import DydxCandleBackendMock


@dataclass
class MockResponse(Response):
    data: Any


class V3PublicMock(Public):
    pass

    def get_candles(
        self,
        market: str,
        resolution: str | None = None,
        from_iso: str | None = None,
        to_iso: str | None = None,
        limit: int | None = None,
    ) -> MockResponse:
        assert resolution, "resolution must be provided when mocking candles."
        assert to_iso, "to_iso must be provided when mocking candles."
        assert from_iso, "from_iso must be provided when mocking candles."

        assert market.find("-") > 0, f"Invalid market: {market}."

        backend = DydxCandleBackendMock()
        data = backend.mock_candles(
            Exchange.DYDX,
            resolution,
            market,
            from_iso,
            to_iso,
            batch_size=100,
        )

        return MockResponse(data=data)


class V3ClientMock(Client):
    def __init__(self) -> None:
        self._public = V3PublicMock(host="", api_timeout=None)

    @property
    def public(self):
        """
        Get the public module, used for interacting with public endpoints.
        """
        return self._public
