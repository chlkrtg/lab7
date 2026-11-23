import asyncio
import logging
import httpx
from app.tasks import long_running_task
from app.storage import get_task

task_queue: asyncio.Queue = asyncio.Queue()


async def send_callback(url: str, payload: dict):
    """Отправляет POST-запрос на callback_url с повторными попытками."""
    max_retries = 3
    async with httpx.AsyncClient() as client:
        for attempt in range(1, max_retries + 1):
            try:
                logging.info(f"Sending callback to {url} (attempt {attempt})")
                response = await client.post(url, json=payload, timeout=5.0)
                response.raise_for_status()
                logging.info(f"Callback sent successfully to {url}")
                return
            except Exception as e:
                logging.warning(f"Callback failed (attempt {attempt}): {e}")
                if attempt < max_retries:
                    await asyncio.sleep(2)
        logging.error(f"Failed to send callback to {url} after {max_retries} attempts")


async def worker():
    logging.info("Worker started")
    while True:
        task_id, input_data, callback_url = await task_queue.get()
        logging.info(f"Worker picked up task {task_id}")

        try:
            await long_running_task(task_id, input_data)

            if callback_url:
                task = get_task(task_id)
                if task and task["status"] == "completed":
                    await send_callback(callback_url, {
                        "task_id": task_id,
                        "status": task["status"],
                        "result": task["result"]
                    })
        except Exception as e:
            logging.error(f"Error in task {task_id}: {e}")
        finally:
            task_queue.task_done()