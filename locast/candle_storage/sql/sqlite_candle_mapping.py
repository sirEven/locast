from decimal import Decimal

from sqlmodel import Session, select


from locast.candle.candle import Candle
from locast.candle_storage.database_candle_mapping import DatabaseCandleMapping
from locast.candle_storage.sql.tables import (
    SqliteCandle,
    SqliteExchange,
    SqliteMarket,
    SqliteResolution,
)


class SqliteCandleMapping(DatabaseCandleMapping):
    def __init__(self, session: Session | None = None) -> None:
        self._session = session
        self._sql_exchange_cache: SqliteExchange | None = None
        self._sql_market_cache: SqliteMarket | None = None
        self._sql_resolution_cache: SqliteResolution | None = None

    def to_candle(self, database_candle: SqliteCandle) -> Candle:
        return Candle(
            id=database_candle.id,
            exchange=database_candle.exchange.exchange,
            market=database_candle.market.market,
            resolution=database_candle.resolution.resolution,
            started_at=database_candle.started_at,
            open=Decimal(database_candle.open),
            high=Decimal(database_candle.high),
            low=Decimal(database_candle.low),
            close=Decimal(database_candle.close),
            base_token_volume=Decimal(database_candle.base_token_volume),
            trades=database_candle.trades,
            usd_volume=Decimal(database_candle.usd_volume),
            starting_open_interest=Decimal(database_candle.starting_open_interest),
        )

    def to_database_candle(self, candle: Candle) -> SqliteCandle:
        if not (
            self._sql_exchange_cache
            and self._sql_market_cache
            and self._sql_resolution_cache
        ):
            assert self._session, "Session must be provided to map to SqliteCandle"
            with self._session as session:
                self._sql_exchange_cache = self._lookup_or_create_sql_exchange(
                    candle,
                    session,
                )
                self._sql_market_cache = self._lookup_or_create_sql_market(
                    candle,
                    session,
                )
                self._sql_resolution_cache = self._lookup_or_create_sql_resolution(
                    candle,
                    session,
                )

        return SqliteCandle(
            id=candle.id,
            exchange=self._sql_exchange_cache,
            market=self._sql_market_cache,
            resolution=self._sql_resolution_cache,
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

    def _lookup_or_create_sql_resolution(
        self,
        candle: Candle,
        session: Session,
    ) -> SqliteResolution:
        sql_resolution = session.exec(
            select(SqliteResolution).filter_by(resolution=candle.resolution)
        ).first()

        if not sql_resolution:
            sql_resolution = SqliteResolution(resolution=candle.resolution)
            session.add(sql_resolution)
            session.commit()
        return sql_resolution

    def _lookup_or_create_sql_market(
        self,
        candle: Candle,
        session: Session,
    ) -> SqliteMarket:
        sql_market = session.exec(
            select(SqliteMarket).filter_by(market=candle.market)
        ).first()

        if not sql_market:
            sql_market = SqliteMarket(market=candle.market)
            session.add(sql_market)
            session.commit()
        return sql_market

    def _lookup_or_create_sql_exchange(
        self,
        candle: Candle,
        session: Session,
    ) -> SqliteExchange:
        sql_exchange = session.exec(
            select(SqliteExchange).filter_by(exchange=candle.exchange)
        ).first()

        if not sql_exchange:
            sql_exchange = SqliteExchange(exchange=candle.exchange)
            session.add(sql_exchange)
            session.commit()
        return sql_exchange
