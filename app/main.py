from contextlib import asynccontextmanager
import asyncio
import logging
from fastapi import FastAPI

from app.config import settings
from app.routers import tasks_router, websocket_router
from app.queue_worker import worker  # импортируем воркер

logging.basicConfig(level=logging.INFO)


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