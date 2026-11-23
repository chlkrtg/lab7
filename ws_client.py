import asyncio
import sys

import websockets


async def main(task_id: str):
    uri = f"ws://127.0.0.1:8000/ws/task/{task_id}"
    async with websockets.connect(uri) as ws:
        async for message in ws:
            print(message)


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1]))