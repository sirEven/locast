from decimal import Decimal
from sqlmodel import Session
from datetime import timezone

from locast.candle.candle import Candle
from locast.candle.exchange import Exchange
from locast.candle.resolution import ResolutionDetail
from locast.candle_storage.database_candle_mapping import DatabaseCandleMapping
from locast.candle_storage.sql.tables import (
    SqliteCandle,
    SqliteExchange,
    SqliteMarket,
    SqliteResolution,
)

from locast.candle_storage.sql.table_utility import TableUtility as tu


class SqliteCandleMapping(DatabaseCandleMapping):
    def __init__(self, session: Session | None = None) -> None:
        self._session = session

        self._sql_exchange_cache: SqliteExchange | None = None
        self._sql_market_cache: SqliteMarket | None = None
        self._sql_resolution_cache: SqliteResolution | None = None

        self._exchange_cache: Exchange | None = None
        self._market_cache: str | None = None
        self._resolution_cache: ResolutionDetail | None = None

    def to_candle(self, database_candle: SqliteCandle) -> Candle:
        try:
            if not self._exchange_cache:
                self._exchange_cache = database_candle.exchange.exchange
            if not self._market_cache:
                self._market_cache = database_candle.market.market
            if not self._resolution_cache:
                self._resolution_cache = ResolutionDetail(
                    database_candle.resolution.seconds,
                    database_candle.resolution.notation,
                )

            return Candle(
                id=database_candle.id,
                exchange=self._exchange_cache,
                market=self._market_cache,
                resolution=self._resolution_cache,
                started_at=database_candle.started_at.replace(tzinfo=timezone.utc),
                open=Decimal(database_candle.open),
                high=Decimal(database_candle.high),
                low=Decimal(database_candle.low),
                close=Decimal(database_candle.close),
                base_token_volume=Decimal(database_candle.base_token_volume),
                trades=database_candle.trades,
                usd_volume=Decimal(database_candle.usd_volume),
                starting_open_interest=Decimal(database_candle.starting_open_interest),
            )
        except Exception as e:
            raise e

    # NOTE: lookup_or_insert funcs are only ever used here, before WRITING to database
    def to_database_candle(self, candle: Candle) -> SqliteCandle:
        try:
            assert self._session, "Session must be provided to map to SqliteCandle."
            with self._session as session:
                if not self._sql_exchange_cache:
                    self._sql_exchange_cache = tu.lookup_or_insert_sqlite_exchange(
                        candle.exchange,
                        session,
                    )
                if not self._sql_market_cache:
                    self._sql_market_cache = tu.lookup_or_insert_sqlite_market(
                        candle.market,
                        session,
                    )
                if not self._sql_resolution_cache:
                    self._sql_resolution_cache = tu.lookup_or_insert_sqlite_resolution(
                        candle.resolution,
                        session,
                    )

                return SqliteCandle(
                    id=candle.id,
                    exchange=self._sql_exchange_cache,
                    exchange_id=self._sql_exchange_cache.id,  # needed for bulk
                    market=self._sql_market_cache,
                    market_id=self._sql_market_cache.id,  # needed for bulk
                    resolution=self._sql_resolution_cache,
                    resolution_id=self._sql_resolution_cache.id,  # needed for bulk
                    started_at=candle.started_at,
                    open=str(candle.open),
                    high=str(candle.high),
                    low=str(candle.low),
                    close=str(candle.close),
                    base_token_volume=str(candle.base_token_volume),
                    trades=candle.trades,
                    usd_volume=str(candle.usd_volume),
                    starting_open_interest=str(candle.starting_open_interest),
                )
        except Exception as e:
            raise e
