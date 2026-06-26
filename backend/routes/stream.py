# backend/routes/stream.py
import asyncio
import json
from fastapi import APIRouter, HTTPException
from starlette.responses import Response
from starlette.types import Receive, Scope, Send
from backend.repositories.room_repo import RoomRepo
from backend.services.sse_manager import sse_manager


router = APIRouter(prefix="/api/rooms", tags=["stream"])


class _SSEStreamingResponse(Response):
    """A minimal ASGI streaming response for SSE.

    Sends headers immediately, then streams body chunks one at a time.
    Does NOT use listen_for_disconnect, avoiding deadlocks with ASGITransport.
    In production (uvicorn), client disconnects are handled via task cancellation.
    """

    def __init__(self, generator, status_code=200, headers=None, media_type=None):
        self._generator = generator
        self.status_code = status_code
        self.media_type = media_type or "text/event-stream"
        self.charset = "utf-8"
        self.background = None
        self.body = b""
        self.raw_headers = []
        if headers:
            for k, v in headers.items():
                self.raw_headers.append(
                    (k.lower().encode("latin-1"), v.encode("latin-1"))
                )
        # Add content-type header
        content_type = self.media_type
        if "charset=" not in content_type.lower():
            content_type += "; charset=" + self.charset
        self.raw_headers.append(
            (b"content-type", content_type.encode("latin-1"))
        )

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        # Send response start immediately
        await send({
            "type": "http.response.start",
            "status": self.status_code,
            "headers": self.raw_headers,
        })

        # Stream body chunks
        try:
            async for chunk in self._generator:
                if isinstance(chunk, str):
                    chunk = chunk.encode(self.charset)
                await send({
                    "type": "http.response.body",
                    "body": chunk,
                    "more_body": True,
                })
        except asyncio.CancelledError:
            pass

        # Signal end of response body
        await send({
            "type": "http.response.body",
            "body": b"",
            "more_body": False,
        })


@router.get("/{room_id}/stream")
async def stream_room(room_id: str):
    room_repo = RoomRepo()
    room = await room_repo.get_by_id(room_id)
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")

    async def event_generator():
        queue = await sse_manager.subscribe(room_id)
        try:
            # Send initial connection event so the headers are flushed
            yield _format_sse("connected", json.dumps({"room_id": room_id}))
            while True:
                message = await queue.get()
                event_type = message["event"]
                data = json.dumps(message["data"], ensure_ascii=False, default=str)
                yield _format_sse(event_type, data)
        except asyncio.CancelledError:
            pass
        finally:
            await sse_manager.unsubscribe(room_id, queue)

    return _SSEStreamingResponse(
        event_generator(),
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


def _format_sse(event: str, data: str) -> str:
    """Format a Server-Sent Event message."""
    return f"event: {event}\ndata: {data}\n\n"
