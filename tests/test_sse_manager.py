# tests/test_sse_manager.py
import pytest
import asyncio
from backend.services.sse_manager import SSEManager


@pytest.mark.asyncio
async def test_subscribe_and_broadcast():
    manager = SSEManager()
    queue = await manager.subscribe("room-1")

    await manager.broadcast("room-1", "test.event", {"msg": "hello"})

    event = await asyncio.wait_for(queue.get(), timeout=1.0)
    assert event["event"] == "test.event"
    assert event["data"] == {"msg": "hello"}


@pytest.mark.asyncio
async def test_room_isolation():
    manager = SSEManager()
    q1 = await manager.subscribe("room-1")
    q2 = await manager.subscribe("room-2")

    await manager.broadcast("room-1", "test", {"room": 1})
    await manager.broadcast("room-2", "test", {"room": 2})

    e1 = await asyncio.wait_for(q1.get(), timeout=1.0)
    e2 = await asyncio.wait_for(q2.get(), timeout=1.0)
    assert e1["data"]["room"] == 1
    assert e2["data"]["room"] == 2


@pytest.mark.asyncio
async def test_unsubscribe():
    manager = SSEManager()
    queue = await manager.subscribe("room-1")
    await manager.unsubscribe("room-1", queue)
    await manager.broadcast("room-1", "test", {})

    # Should not receive — queue was removed
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(queue.get(), timeout=0.3)


@pytest.mark.asyncio
async def test_broadcast_removes_disconnected_queues():
    manager = SSEManager()
    manager._channels["room-1"] = set()
    # Add a mock queue that raises on put
    class BrokenQueue:
        async def put(self, item):
            raise RuntimeError("disconnected")
    broken = BrokenQueue()
    manager._channels["room-1"].add(broken)

    # Should not raise
    await manager.broadcast("room-1", "test", {})
    assert broken not in manager._channels["room-1"]
