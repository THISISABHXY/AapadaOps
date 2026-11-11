"""AapadaOps Real-Time WebSocket Streaming Endpoints."""

import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.websocket_manager import ws_manager

logger = logging.getLogger("AapadaOps.WebSockets")
router = APIRouter(tags=["WebSockets"])


@router.websocket("/ws/{channel}")
async def websocket_channel_endpoint(websocket: WebSocket, channel: str):
    """Real-time operational streaming channel for incidents, alerts, tasks, and coordination."""
    await ws_manager.connect(websocket, channel)
    try:
        while True:
            # Keep socket alive and listen for client ping/messages
            data = await websocket.receive_text()
            # Echo heartbeat ping-pong
            if data.strip().lower() == "ping":
                await websocket.send_text('{"event": "PONG"}')
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, channel)
    except Exception as exc:
        logger.warning(f"WebSocket error on channel '{channel}': {exc}")
        ws_manager.disconnect(websocket, channel)

