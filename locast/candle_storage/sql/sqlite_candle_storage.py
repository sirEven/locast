from typing import List, Tuple
from sqlalchemy import Engine

from sqlmodel import SQLModel, Session, asc, desc, select, func

from locast.candle.candle import Candle
from locast.candle.exchange import Exchange
from locast.candle.resolution import Seconds
from locast.candle_storage.candle_storage import CandleStorage
from locast.candle_storage.cluster_info import ClusterInfo
from locast.candle_storage.database_candle_mapper import DatabaseCandleMapper
from locast.candle_storage.sql.sqlite_candle_mapping import SqliteCandleMapping
from locast.candle_storage.sql.tables import (
    SqliteCandle,
    SqliteExchange,
    SqliteMarket,
    SqliteResolution,
)

from locast.candle_storage.sql.table_utility import TableUtility as tu
from locast.candle.candle_utility import CandleUtility as cu


class SqliteCandleStorage(CandleStorage):
    def __init__(self, engine: Engine) -> None:
        self._engine = engine
        SQLModel.metadata.create_all(self._engine)

    async def store_candles(self, candles: List[Candle]) -> None:
        with Session(self._engine) as session:
            mapper = DatabaseCandleMapper(SqliteCandleMapping(session))
            for candle in candles:
                session.add(mapper.to_database_candle(candle))
            session.commit()

    async def retrieve_candles(
        self,
        exchange: Exchange,
        market: str,
        resolution: Seconds,
    ) -> List[Candle]:
        with Session(self._engine) as session:
            sql_exchange = tu.lookup_sqlite_exchange(exchange, session)
            sql_market = tu.lookup_sqlite_market(market, session)
            sql_resolution = tu.lookup_sqlite_resolution(resolution, session)

            assert sql_exchange, f"Exchange {exchange} not found in database."
            assert sql_market, f"Market {market} not found in database."
            assert sql_resolution, f"Resolution {resolution} not found in database."

            statement = select(SqliteCandle).where(
                (SqliteCandle.exchange_id == sql_exchange.id)
                & (SqliteCandle.market_id == sql_market.id)
                & (SqliteCandle.resolution_id == sql_resolution.id)
            )

            results = session.exec(statement)
            return self._to_candles(list(results.all()))

    # TODO: Rename this func
    async def get_cluster_info(
        self,
        exchange: Exchange,
        market: str,
        resolution: Seconds,
    ) -> ClusterInfo | None:
        result: ClusterInfo | None = None
        with Session(self._engine) as session:
            if sqlite_properties := self._look_up_foreign_values(
                exchange,
                market,
                resolution,
                session,
            ):
                sqlite_exchange, sqlite_market, sqlite_resolution = sqlite_properties

                if head_and_tail := self._query_head_and_tail(
                    sqlite_exchange,
                    sqlite_market,
                    sqlite_resolution,
                    session,
                ):
                    head, tail = head_and_tail
                    amount = self._query_amount(
                        sqlite_exchange,
                        sqlite_market,
                        sqlite_resolution,
                        session,
                    )
                    is_uptodate = cu.is_newest_valid_candle(head)
                    if head and amount:
                        result = ClusterInfo(head, tail, amount, is_uptodate)
        return result

    def _to_candles(self, database_candles: List[SqliteCandle]) -> List[Candle]:
        mapper = DatabaseCandleMapper(SqliteCandleMapping())
        return [mapper.to_candle(sqlite_candle) for sqlite_candle in database_candles]

    def _look_up_foreign_values(
        self,
        exchange: Exchange,
        market: str,
        resolution: Seconds,
        session: Session,
    ) -> Tuple[SqliteExchange, SqliteMarket, SqliteResolution] | None:
        sqlite_exchange = tu.lookup_sqlite_exchange(exchange, session)
        sqlite_market = tu.lookup_sqlite_market(market, session)
        sqlite_resolution = tu.lookup_sqlite_resolution(resolution, session)

        if not (sqlite_exchange and sqlite_market and sqlite_resolution):
            return None

        return sqlite_exchange, sqlite_market, sqlite_resolution

    def _query_head_and_tail(
        self,
        sqlite_exchange: SqliteExchange,
        sqlite_market: SqliteMarket,
        sqlite_resolution: SqliteResolution,
        session: Session,
    ) -> Tuple[Candle, Candle] | None:
        head = self._query_head(
            sqlite_exchange,
            sqlite_market,
            sqlite_resolution,
            session,
        )

        tail = self._query_tail(
            sqlite_exchange,
            sqlite_market,
            sqlite_resolution,
            session,
        )

        return (head, tail) if head and tail else None

    def _query_head(
        self,
        sqlite_exchange: SqliteExchange,
        sqlite_market: SqliteMarket,
        sqlite_resolution: SqliteResolution,
        session: Session,
    ) -> Candle | None:
        head_statement = (
            select(SqliteCandle)
            .where(
                (SqliteCandle.exchange_id == sqlite_exchange.id)
                & (SqliteCandle.market_id == sqlite_market.id)
                & (SqliteCandle.resolution_id == sqlite_resolution.id)
            )
            .order_by(desc(SqliteCandle.started_at))
            .limit(1)
        )

        head: Candle | None = None

        if head_results := session.exec(head_statement).first():
            head = self._to_candles([head_results])[0]

        return head

    def _query_tail(
        self,
        sqlite_exchange: SqliteExchange,
        sqlite_market: SqliteMarket,
        sqlite_resolution: SqliteResolution,
        session: Session,
    ) -> Candle | None:
        tail_statement = (
            select(SqliteCandle)
            .where(
                (SqliteCandle.exchange_id == sqlite_exchange.id)
                & (SqliteCandle.market_id == sqlite_market.id)
                & (SqliteCandle.resolution_id == sqlite_resolution.id)
            )
            .order_by(asc(SqliteCandle.started_at))
            .limit(1)
        )

        tail: Candle | None = None

        if tail_results := session.exec(tail_statement).first():
            tail = self._to_candles([tail_results])[0]

        return tail

    def _query_amount(
        self,
        sqlite_exchange: SqliteExchange,
        sqlite_market: SqliteMarket,
        sqlite_resolution: SqliteResolution,
        session: Session,
    ) -> int | None:
        statement = select(SqliteCandle).where(
            (SqliteCandle.exchange_id == sqlite_exchange.id)
            & (SqliteCandle.market_id == sqlite_market.id)
            & (SqliteCandle.resolution_id == sqlite_resolution.id)
        )

        count_query = (
            statement.with_only_columns(func.count())
            .order_by(None)
            .select_from(statement.get_final_froms()[0])
        )

        return session.scalar(count_query)
