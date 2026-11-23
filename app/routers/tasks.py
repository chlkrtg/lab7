import asyncio
import logging
from app.queue_worker import task_queue
from app.tasks import sync_cpu_bound
from fastapi import APIRouter, BackgroundTasks, HTTPException
from app.storage import create_task, get_task

from pydantic import BaseModel
from typing import Optional


class ProcessRequest(BaseModel):
    name: str
    callback_url: Optional[str] = None


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/tasks", tags=["long tasks"])


# ---------- Задание 2: фоновый email ----------
@router.post("/email")
async def notify_email(
        email: str,
        message: str,
        background_tasks: BackgroundTasks,
):
    def send_email(email: str, message: str):
        import time
        time.sleep(2)
        print(f"Email sent to {email}: {message}")

    background_tasks.add_task(send_email, email, message)
    return {"status": "email will be sent in background"}


# ---------- Задание 6: очередь задач ----------
@router.post("/process")
async def start_processing(request: ProcessRequest):
    task_id = create_task()
    logger.info(f"Task {task_id} created and queued (callback_url={request.callback_url})")
    await task_queue.put((task_id, {"name": request.name}, request.callback_url))
    return {"task_id": task_id, "status": "queued"}


@router.get("/{task_id}")
async def get_task_status(task_id: str):
    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


# ---------- Задание 4: синхронный код в асинхронном контексте ----------
@router.post("/compute")
async def compute_sync(data: dict):
    result = await asyncio.to_thread(sync_cpu_bound, data)
    return result
