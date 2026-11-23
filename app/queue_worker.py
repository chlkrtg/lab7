import asyncio
import logging
from app.tasks import long_running_task

# Создаём очередь
task_queue: asyncio.Queue = asyncio.Queue()


async def worker():
    """
    Бесконечный цикл, который забирает задачи из очереди
    и выполняет их по одной.
    """
    logging.info("Worker started")
    while True:
        task_id, input_data = await task_queue.get()
        logging.info(f"Worker picked up task {task_id}")

        try:
            await long_running_task(task_id, input_data)
        except Exception as e:
            logging.error(f"Error in task {task_id}: {e}")
        finally:
            task_queue.task_done()