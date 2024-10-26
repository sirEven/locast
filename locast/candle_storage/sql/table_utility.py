from sqlmodel import (
    Session,
    select,  # type: ignore
)
from locast.candle.exchange import Exchange
from locast.candle.exchange_resolution import ResolutionDetail
from locast.candle_storage.sql.tables import (
    SqliteExchange,
    SqliteMarket,
    SqliteResolution,
)


class TableUtility:
    @staticmethod
    def lookup_sqlite_exchange(
        exchange: Exchange,
        session: Session,
    ) -> SqliteExchange | None:
        return session.exec(select(SqliteExchange).filter_by(exchange=exchange)).first()

    @staticmethod
    def lookup_sqlite_market(market: str, session: Session) -> SqliteMarket | None:
        return session.exec(select(SqliteMarket).filter_by(market=market)).first()

    @staticmethod
    def lookup_sqlite_resolution(
        resolution: ResolutionDetail,
        session: Session,
    ) -> SqliteResolution | None:
        return session.exec(
            select(SqliteResolution).filter_by(
                seconds=resolution.seconds,
                notation=resolution.notation,
            )
        ).first()

    @staticmethod
    def lookup_or_insert_sqlite_exchange(
        exchange: Exchange,
        session: Session,
    ) -> SqliteExchange:
        sql_exchange = TableUtility.lookup_sqlite_exchange(
            exchange=exchange,
            session=session,
        )

        if not sql_exchange:
            sql_exchange = SqliteExchange(exchange=exchange)
            session.add(sql_exchange)
            session.commit()
        return sql_exchange

    @staticmethod
    def lookup_or_insert_sqlite_market(
        market: str,
        session: Session,
    ) -> SqliteMarket:
        sql_market = TableUtility.lookup_sqlite_market(market=market, session=session)

        if not sql_market:
            sql_market = SqliteMarket(market=market)
            session.add(sql_market)
            session.commit()
        return sql_market

    @staticmethod
    def lookup_or_insert_sqlite_resolution(
        resolution: ResolutionDetail,
        session: Session,
    ) -> SqliteResolution:
        sql_resolution = TableUtility.lookup_sqlite_resolution(
            resolution=resolution,
            session=session,
        )

        if not sql_resolution:
            sql_resolution = SqliteResolution(
                seconds=resolution.seconds,
                notation=resolution.notation,
            )
            session.add(sql_resolution)
            session.commit()
        return sql_resolution
