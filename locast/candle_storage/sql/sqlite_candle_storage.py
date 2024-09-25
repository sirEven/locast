from typing import List, Tuple
from sqlalchemy import Engine, and_, delete, literal

from sqlmodel import SQLModel, Session, asc, desc, select, func

from locast.candle.candle_utility import CandleUtility as cu
from locast.candle.candle import Candle
from locast.candle.exchange import Exchange
from locast.candle.resolution import ResolutionDetail
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


class SqliteCandleStorage(CandleStorage):
    def __init__(self, engine: Engine) -> None:
        self._engine = engine
        SQLModel.metadata.create_all(self._engine)

    async def store_candles(self, candles: List[Candle]) -> None:
        # NOTE: Benchmarking showed stable, scalable results across different amounts with a batch size of 5k
        await self._bulk_save_objects_batched(candles, 5000)

    async def _bulk_save_objects_batched(
        self,
        candles: List[Candle],
        batch_size: int,
    ) -> None:
        total_candles = len(candles)
        num_batches = (total_candles + batch_size - 1) // batch_size  # Ceiling division

        for i in range(num_batches):
            # Get the current batch of candles
            batch = candles[i * batch_size : (i + 1) * batch_size]

            # Create a new session for this batch
            with Session(self._engine) as session:
                # Initialize mapper with the current session
                mapper = DatabaseCandleMapper(SqliteCandleMapping(session))

                # Perform bulk insert
                session.bulk_save_objects(
                    [mapper.to_database_candle(candle) for candle in batch]
                )
                session.commit()

    async def retrieve_cluster(
        self,
        exchange: Exchange,
        market: str,
        resolution: ResolutionDetail,
    ) -> List[Candle]:
        with Session(self._engine) as session:
            if foreign_keys := self._look_up_foreign_keys(
                exchange,
                market,
                resolution,
                session,
            ):
                sqlite_exchange, sqlite_market, sqlite_resolution = foreign_keys

                stmnt = (
                    select(SqliteCandle)
                    .where(
                        (SqliteCandle.exchange_id == sqlite_exchange.id)
                        & (SqliteCandle.market_id == sqlite_market.id)
                        & (SqliteCandle.resolution_id == sqlite_resolution.id)
                    )
                    .order_by(desc(SqliteCandle.started_at))
                )

                results = session.exec(stmnt)
                return self._to_candles(list(results.all()))
            else:
                return []

    async def delete_cluster(
        self,
        exchange: Exchange,
        market: str,
        resolution: ResolutionDetail,
    ) -> None:
        with Session(self._engine) as session:
            if foreign_keys := self._look_up_foreign_keys(
                exchange,
                market,
                resolution,
                session,
            ):
                sqlite_exchange, sqlite_market, sqlite_resolution = foreign_keys

                stmt = delete(SqliteCandle).where(
                    and_(
                        literal(sqlite_exchange.id) == SqliteCandle.exchange_id,
                        literal(sqlite_market.id) == SqliteCandle.market_id,
                        literal(sqlite_resolution.id) == SqliteCandle.resolution_id,
                    )
                )

                with self._engine.begin() as conn:
                    conn.execute(stmt)

                session.commit()

    async def get_cluster_info(
        self,
        exchange: Exchange,
        market: str,
        resolution: ResolutionDetail,
    ) -> ClusterInfo:
        result = ClusterInfo(None, None, 0, False)
        with Session(self._engine) as session:
            if foreign_keys := self._look_up_foreign_keys(
                exchange,
                market,
                resolution,
                session,
            ):
                sqlite_exchange, sqlite_market, sqlite_resolution = foreign_keys

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

    def _look_up_foreign_keys(
        self,
        exchange: Exchange,
        market: str,
        resolution: ResolutionDetail,
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
        stmnt = select(SqliteCandle).where(
            (SqliteCandle.exchange_id == sqlite_exchange.id)
            & (SqliteCandle.market_id == sqlite_market.id)
            & (SqliteCandle.resolution_id == sqlite_resolution.id)
        )

        count_query = (
            stmnt.with_only_columns(func.count())
            .order_by(None)
            .select_from(stmnt.get_final_froms()[0])
        )

        return session.scalar(count_query)
