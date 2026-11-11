"""AapadaOps Real-Time WebSocket Connection Manager."""

import json
import logging
from typing import Dict, List, Set
from fastapi import WebSocket

logger = logging.getLogger("AapadaOps.WebSockets")


class WebSocketManager:
    """Manages active WebSocket connections grouped by operational topic channels."""

    def __init__(self):
        # Maps channel name (e.g., 'incidents', 'alerts', 'tasks') -> set of WebSockets
        self.active_channels: Dict[str, Set[WebSocket]] = {
            "incidents": set(),
            "alerts": set(),
            "tasks": set(),
            "coordination": set(),
        }

    async def connect(self, websocket: WebSocket, channel: str = "incidents"):
        """Accept WebSocket and subscribe to channel."""
        await websocket.accept()
        if channel not in self.active_channels:
            self.active_channels[channel] = set()
        self.active_channels[channel].add(websocket)
        logger.info(f"WebSocket client connected to channel '{channel}'. Active: {len(self.active_channels[channel])}")

    def disconnect(self, websocket: WebSocket, channel: str = "incidents"):
        """Remove WebSocket connection on client exit."""
        if channel in self.active_channels and websocket in self.active_channels[channel]:
            self.active_channels[channel].remove(websocket)
            logger.info(f"WebSocket client disconnected from channel '{channel}'. Remaining: {len(self.active_channels[channel])}")

    async def broadcast(self, channel: str, message: dict):
        """Broadcast JSON message to all subscribers of a specific channel."""
        if channel not in self.active_channels:
            return

        dead_sockets: List[WebSocket] = []
        payload = json.dumps(message)

        for connection in self.active_channels[channel]:
            try:
                await connection.send_text(payload)
            except Exception as exc:
                logger.warning(f"Failed to send to WebSocket in channel '{channel}': {exc}")
                dead_sockets.append(connection)

        # Cleanup dropped connections
        for dead in dead_sockets:
            if dead in self.active_channels[channel]:
                self.active_channels[channel].remove(dead)


ws_manager = WebSocketManager()

