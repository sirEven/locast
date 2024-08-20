from sqlmodel import (
    Session,
    select,  # type: ignore
)
from locast.candle.exchange import Exchange
from locast.candle.resolution import Seconds
from locast.candle_storage.sql.tables import (
    SqliteExchange,
    SqliteMarket,
    SqliteResolution,
)


class TableAccess:
    @staticmethod
    def lookup_sql_exchange(
        exchange: Exchange,
        session: Session,
    ) -> SqliteExchange | None:
        return session.exec(select(SqliteExchange).filter_by(exchange=exchange)).first()

    @staticmethod
    def lookup_sql_market(market: str, session: Session) -> SqliteMarket | None:
        return session.exec(select(SqliteMarket).filter_by(market=market)).first()

    @staticmethod
    def lookup_sql_resolution(
        resolution: Seconds, session: Session
    ) -> SqliteResolution | None:
        return session.exec(
            select(SqliteResolution).filter_by(resolution=resolution)
        ).first()

    @staticmethod
    def lookup_or_create_sql_resolution(
        resolution: Seconds, session: Session
    ) -> SqliteResolution:
        sql_resolution = TableAccess.lookup_sql_resolution(
            resolution=resolution,
            session=session,
        )

        if not sql_resolution:
            sql_resolution = SqliteResolution(resolution=resolution)
            session.add(sql_resolution)
            session.commit()
        return sql_resolution

    @staticmethod
    def lookup_or_create_sql_market(
        market: str,
        session: Session,
    ) -> SqliteMarket:
        sql_market = TableAccess.lookup_sql_market(market=market, session=session)

        if not sql_market:
            sql_market = SqliteMarket(market=market)
            session.add(sql_market)
            session.commit()
        return sql_market

    @staticmethod
    def lookup_or_create_sql_exchange(
        exchange: Exchange,
        session: Session,
    ) -> SqliteExchange:
        sql_exchange = TableAccess.lookup_sql_exchange(
            exchange=exchange,
            session=session,
        )

        if not sql_exchange:
            sql_exchange = SqliteExchange(exchange=exchange)
            session.add(sql_exchange)
            session.commit()
        return sql_exchange
