import os
from typing import Dict, List, Optional, Set

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
            CREATE TABLE IF NOT EXISTS scrappings_previas_operacionais (
                id           SERIAL PRIMARY KEY,
                nome_empresa TEXT NOT NULL,
                url          TEXT NOT NULL,
                trimestre    TEXT NOT NULL,
                is_concluido BOOLEAN DEFAULT FALSE
            )
            """
        )
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS lancamentos_vendas_empresas (
                id           BIGSERIAL PRIMARY KEY,
                nome_empresa VARCHAR(100) NOT NULL,
                trimestre    VARCHAR(10) NOT NULL,
                tipo         VARCHAR(20) NOT NULL,
                valor        NUMERIC
            )
            """
        )


async def get_existing_urls() -> Set[str]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT url FROM scrappings_previas_operacionais")
    return {row["url"] for row in rows}


async def insert_scrap(item: Dict[str, str]) -> None:
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO scrappings_previas_operacionais (nome_empresa, url, trimestre)
            VALUES ($1, $2, $3)
            """,
            item["nome_empresa"],
            item["url"],
            item["trimestre_ano"],
        )


async def get_pending_scraps() -> List[asyncpg.Record]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT id, nome_empresa, url, trimestre
            FROM scrappings_previas_operacionais
            WHERE is_concluido IS FALSE OR is_concluido IS NULL
            """
        )
    return rows


async def insert_balanco(
    nome_empresa: str, trimestre: str, tipo: str, valor: Optional[float]
) -> None:
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO lancamentos_vendas_empresas (nome_empresa, trimestre, tipo, valor)
            VALUES ($1, $2, $3, $4)
            """,
            nome_empresa,
            trimestre,
            tipo,
            valor,
        )


async def mark_concluido(scrap_id: int) -> None:
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            """
            UPDATE scrappings_previas_operacionais
            SET is_concluido = TRUE
            WHERE id = $1
            """,
            scrap_id,
        )


async def get_balanco(
    nome_empresa: str, trimestre: str, tipo: str
) -> Optional[asyncpg.Record]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT id, nome_empresa, trimestre, tipo, valor
            FROM lancamentos_vendas_empresas
            WHERE nome_empresa = $1 AND trimestre = $2 AND tipo = $3
            ORDER BY id DESC
            LIMIT 1
            """,
            nome_empresa,
            trimestre,
            tipo,
        )
    return row
