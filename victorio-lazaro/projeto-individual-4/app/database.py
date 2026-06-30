import os
from typing import Dict, Set

import asyncpg

_pool: asyncpg.Pool | None = None


async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        database_url = os.getenv(
            "DATABASE_URL",
            "postgresql://scrapper:scrapper123@db:5432/scrapper_db",
        )
        _pool = await asyncpg.create_pool(database_url)
    return _pool


async def init_db() -> None:
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS scrappings_previas_operacionas (
                id           SERIAL PRIMARY KEY,
                nome_empresa TEXT NOT NULL,
                url          TEXT NOT NULL,
                trimestre_ano TEXT NOT NULL
            )
            """
        )


async def get_existing_urls() -> Set[str]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT url FROM scrappings_previas_operacionas")
    return {row["url"] for row in rows}


async def insert_scrap(item: Dict[str, str]) -> None:
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO scrappings_previas_operacionas (nome_empresa, url, trimestre_ano)
            VALUES ($1, $2, $3)
            """,
            item["nome_empresa"],
            item["url"],
            item["trimestre_ano"],
        )
