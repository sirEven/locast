import asyncio

from locast.candle_storage.sql.candle_model import create_db_and_tables


async def main():
    create_db_and_tables()


asyncio.run(main())
