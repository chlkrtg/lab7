import asyncio

from fastapi import APIRouter, BackgroundTasks, HTTPException

from app.storage import create_task, get_task
from app.tasks import long_running_task, sync_cpu_bound

from fastapi import APIRouter, BackgroundTasks, HTTPException

from app.storage import create_task, get_task
from app.tasks import long_running_task

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


# ---------- Задание 3: длительная задача с polling ----------
@router.post("/process")
async def start_processing(
        input_data: dict,
        background_tasks: BackgroundTasks,
):
    task_id = create_task()
    # Запускаем фоновую задачу (не блокирует ответ)
    background_tasks.add_task(long_running_task, task_id, input_data)
    return {"task_id": task_id}


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
