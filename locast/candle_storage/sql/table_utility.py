from sqlmodel import (
    Session,
    select,
)
from locast.candle.exchange import Exchange
from locast.candle.resolution import Seconds
from locast.candle_storage.sql.tables import (
    SqliteExchange,
    SqliteMarket,
    SqliteResolution,
)


class TableAccess:
    @classmethod
    def get_exchange_id(cls, exchange: Exchange, session: Session) -> int:
        # Check if "exchange" table already exists in the db - if not, add it
        stmnt = select(SqliteExchange).where(SqliteExchange.exchange == exchange)
        exchange_obj = session.exec(stmnt).first()

        if not exchange_obj:
            exchange_obj = SqliteExchange(exchange=exchange)
            session.add(exchange_obj)
            session.commit()
        assert exchange_obj.id
        return exchange_obj.id

    @classmethod
    def get_exchange(cls, exchange_id: int, session: Session) -> Exchange | None:
        with session:
            stmnt = select(SqliteExchange).where(SqliteExchange.id == exchange_id)
            if exchange_table := session.exec(stmnt).first():
                return exchange_table.exchange
            else:
                return None

    @classmethod
    def get_market_id(cls, market: str, session: Session) -> int:
        # Check if "market" table already exists in the db - if not, add it
        stmnt = select(SqliteMarket).where(SqliteMarket.market == market)
        market_obj = session.exec(stmnt).first()

        if not market_obj:
            market_obj = SqliteMarket(market=market)
            session.add(market_obj)
            session.commit()
        assert market_obj.id
        return market_obj.id

    @classmethod
    def get_market(cls, market_id: int, session: Session) -> str | None:
        with session:
            stmnt = select(SqliteMarket).where(SqliteMarket.id == market_id)
            if sql_market := session.exec(stmnt).first():
                return sql_market.market
            else:
                return None

    @classmethod
    def get_resolution_id(cls, resolution: Seconds, session: Session) -> int:
        # Check if the "resolution" table already exists in the table - if not, add it
        stmnt = select(SqliteResolution).where(
            SqliteResolution.resolution == resolution
        )
        resolution_obj = session.exec(stmnt).first()
        if not resolution_obj:
            resolution_obj = SqliteResolution(resolution=resolution)
            session.add(resolution_obj)
            session.commit()
        assert resolution_obj.id
        return resolution_obj.id

    @classmethod
    def get_resolution(cls, resolution_id: int, session: Session) -> Seconds | None:
        with session:
            stmnt = select(SqliteResolution).where(SqliteResolution.id == resolution_id)
            if sql_resolution := session.exec(stmnt).first():
                return sql_resolution.resolution
            else:
                return None
