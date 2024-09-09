import pytest
from sqlmodel import Session
from locast.candle.exchange import Exchange
from locast.candle_storage.sql.sqlite_candle_mapping import SqliteCandleMapping
from tests.helper.candle_mockery.mock_candle import mock_candle


def test_to_database_candle_results_in_error(sqlite_session_in_memory: Session) -> None:
    # given
    mapping = SqliteCandleMapping(sqlite_session_in_memory)

    # when mapping is performed without prior Storage initialization,then
    with pytest.raises(Exception):
        mapping.to_database_candle(mock_candle(Exchange.DYDX_V4))
