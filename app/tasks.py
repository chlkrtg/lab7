import asyncio
import time
import logging

from app.storage import update_task

logger = logging.getLogger(__name__)


async def long_running_task(task_id: str, input_data: dict):
    logger.info(f"Task {task_id} started processing")
    try:
        total_steps = 10
        for step in range(1, total_steps + 1):
            await asyncio.sleep(1)
            await update_task(task_id, "running", {"progress": step, "total": total_steps})
            # Логируем прогресс (можно раз в 5 шагов, чтобы не спамить)
            if step % 5 == 0 or step == total_steps:
                logger.info(f"Task {task_id} progress: {step}/{total_steps}")

        result = {"output": f"Processed {input_data.get('name', 'unknown')}"}
        await update_task(task_id, "completed", result)
        logger.info(f"Task {task_id} completed successfully")
    except Exception as e:
        logger.error(f"Task {task_id} failed: {e}", exc_info=True)
        await update_task(task_id, "error", {"error": str(e)})


def sync_cpu_bound(data: dict) -> dict:
    # Имитация вычислений, занимающих несколько секунд
    time.sleep(3)  # блокирующий вызов
    return {"computed": data.get("value", 0) * 2}
