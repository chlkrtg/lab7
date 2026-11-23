import json
import logging
from typing import Any, Optional
from uuid import uuid4
import redis.asyncio as redis
from app.config import settings

logger = logging.getLogger(__name__)

redis_client = redis.from_url(settings.redis_url, decode_responses=True)

async def create_task() -> str:
    task_id = str(uuid4())
    initial_state = {"status": "pending", "result": None}
    await redis_client.setex(
        f"task:{task_id}",
        settings.task_ttl_seconds,
        json.dumps(initial_state)
    )
    logger.info(f"Task {task_id} created in Redis")
    return task_id

async def update_task(task_id: str, status: str, result: Any = None):
    key = f"task:{task_id}"
    data = await redis_client.get(key)
    if not data:
        return
    task = json.loads(data)
    task["status"] = status
    if result is not None:
        task["result"] = result
    await redis_client.setex(key, settings.task_ttl_seconds, json.dumps(task))

async def get_task(task_id: str) -> Optional[dict]:
    data = await redis_client.get(f"task:{task_id}")
    if not data:
        return None
    return json.loads(data)