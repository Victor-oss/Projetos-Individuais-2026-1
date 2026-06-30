import asyncio
import logging
import re
import sys
import os
from contextlib import asynccontextmanager
from enum import Enum
from typing import Literal

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI, HTTPException, Query

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from scrapper import main as run_scrapper  # noqa: E402
from app.database import (
    get_balanco,
    get_existing_urls,
    get_pending_scraps,
    init_db,
    insert_balanco,
    insert_scrap,
    mark_concluido,
)
from app.pdf_processor import extract_balanco_from_pdf

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

EMPRESAS_VALIDAS = {"MRV", "Pacaembu", "Plano & Plano", "Tenda", "Cury", "Direcional"}
TRIMESTRE_PATTERN = re.compile(r"^[1-4]/\d{4}$")


async def process_pending_pdfs() -> None:
    logger.info("Processing pending PDFs...")
    pending = await get_pending_scraps()
    processed = 0

    for record in pending:
        scrap_id = record["id"]
        nome_empresa = record["nome_empresa"]
        trimestre = record["trimestre"]
        url = record["url"]

        try:
            balanco = await extract_balanco_from_pdf(url)

            await insert_balanco(nome_empresa, trimestre, "LANCAMENTO", balanco.total_lancamentos)
            await insert_balanco(nome_empresa, trimestre, "VENDA", balanco.total_vendas)
            await mark_concluido(scrap_id)
            processed += 1
            logger.info("Processed PDF for %s %s", nome_empresa, trimestre)
        except Exception:
            logger.exception("Failed to process PDF id=%d url=%s", scrap_id, url)

    logger.info("PDF processing done. %d records processed.", processed)


async def scrape_and_store() -> None:
    logger.info("Starting scraping job...")
    try:
        results = await run_scrapper()
        existing_urls = await get_existing_urls()

        inserted = 0
        for item in results:
            if item["url"] and item["url"] not in existing_urls:
                await insert_scrap(item)
                existing_urls.add(item["url"])
                inserted += 1

        logger.info("Scraping done. %d new records inserted.", inserted)
    except Exception:
        logger.exception("Scraping job failed.")

    await process_pending_pdfs()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    scheduler.add_job(scrape_and_store, "interval", minutes=10, id="scrape_job")
    scheduler.start()
    asyncio.create_task(scrape_and_store())
    yield
    scheduler.shutdown()


app = FastAPI(title="Prévias Operacionais Scraper", lifespan=lifespan)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/scrape")
async def trigger_scrape():
    asyncio.create_task(scrape_and_store())
    return {"message": "Scraping job triggered"}


@app.get("/balanco")
async def balanco_endpoint(
    nome_empresa: str = Query(..., description="Nome da empresa"),
    trimestre: str = Query(..., description="Trimestre no formato {trimestre}/{ano}"),
    tipo: str = Query(..., description="Tipo: LANCAMENTO ou VENDA"),
):
    if nome_empresa not in EMPRESAS_VALIDAS:
        raise HTTPException(
            status_code=422,
            detail=f"nome_empresa inválido. Valores aceitos: {', '.join(sorted(EMPRESAS_VALIDAS))}",
        )

    if not TRIMESTRE_PATTERN.match(trimestre):
        raise HTTPException(
            status_code=422,
            detail="trimestre inválido. Formato esperado: {trimestre}/{ano} (ex: 2/2025)",
        )

    if tipo not in ("LANCAMENTO", "VENDA"):
        raise HTTPException(
            status_code=422,
            detail="tipo inválido. Valores aceitos: LANCAMENTO, VENDA",
        )

    record = await get_balanco(nome_empresa, trimestre, tipo)

    if record is None:
        raise HTTPException(status_code=404, detail="Registro não encontrado")

    return {
        "id": record["id"],
        "nome_empresa": record["nome_empresa"],
        "trimestre": record["trimestre"],
        "tipo": record["tipo"],
        "valor": float(record["valor"]) if record["valor"] is not None else None,
    }
