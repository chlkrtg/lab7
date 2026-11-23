from contextlib import asynccontextmanager
import asyncio
import logging
from fastapi import FastAPI

from app.config import settings
from app.routers import tasks_router, websocket_router
from app.queue_worker import worker  # импортируем воркер

# --- Настройка логирования (6.3) ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logging.getLogger("httpx").setLevel(logging.WARNING)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Starting background worker...")
    worker_task = asyncio.create_task(worker())
    yield
    logging.info("Shutting down background worker...")
    worker_task.cancel()


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.include_router(tasks_router)
app.include_router(websocket_router)


@app.get("/")
async def root():
    return {"message": "Hello, Async FastAPI!"}
