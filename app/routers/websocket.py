import asyncio
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.storage import get_task

logger = logging.getLogger(__name__)
router = APIRouter(tags=["websocket"])

@router.websocket("/ws/task/{task_id}")
async def websocket_task_status(websocket: WebSocket, task_id: str):
    await websocket.accept()
    logger.info(f"WebSocket connected for task {task_id}")
    try:
        while True:
            task = get_task(task_id)
            if not task:
                await websocket.send_json({"error": "Task not found"})
                break
            await websocket.send_json(task)
            if task["status"] in ("completed", "error"):
                logger.info(f"WebSocket closing: task {task_id} is {task['status']}")
                break
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        logger.warning(f"WebSocket client disconnected unexpectedly for task {task_id}")
    finally:
        try:
            await websocket.close()
        except RuntimeError:
            pass