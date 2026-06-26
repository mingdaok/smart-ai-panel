# backend/services/sse_manager.py
import asyncio
import logging

logger = logging.getLogger(__name__)


class SSEManager:
    def __init__(self):
        self._channels: dict[str, set[asyncio.Queue]] = {}

    async def subscribe(self, room_id: str) -> asyncio.Queue:
        queue: asyncio.Queue = asyncio.Queue()
        self._channels.setdefault(room_id, set()).add(queue)
        return queue

    async def unsubscribe(self, room_id: str, queue: asyncio.Queue):
        if room_id in self._channels:
            self._channels[room_id].discard(queue)
            if not self._channels[room_id]:
                del self._channels[room_id]

    async def broadcast(self, room_id: str, event_type: str, data: dict):
        if room_id not in self._channels:
            return
        message = {"event": event_type, "data": data}
        dead_queues = set()
        for queue in self._channels[room_id]:
            try:
                await queue.put(message)
            except Exception:
                dead_queues.add(queue)
        self._channels[room_id] -= dead_queues


# Singleton
sse_manager = SSEManager()
