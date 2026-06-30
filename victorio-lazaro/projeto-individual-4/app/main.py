import asyncio
import logging
import sys
import os
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from scrapper import main as run_scrapper  # noqa: E402
from app.database import get_existing_urls, init_db, insert_scrap  # noqa: E402

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

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
