import hmac
import logging
from typing import List

from fastapi import WebSocket, WebSocketDisconnect

from app.config import get_settings

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections with token-based authentication."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> bool:
        """Accept connection if valid ?token=API_KEY query param."""
        token = websocket.query_params.get("token")
        if not token:
            await websocket.close(code=1008)
            return False

        settings = get_settings()
        if not hmac.compare_digest(token, settings.API_KEY):
            await websocket.close(code=1008)
            return False

        await websocket.accept()
        self.active_connections.append(websocket)
        return True

    def disconnect(self, websocket: WebSocket) -> None:
        """Remove websocket from active connections."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict) -> None:
        """Send JSON message to all connected clients."""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(connection)
        for conn in disconnected:
            self.disconnect(conn)


manager = ConnectionManager()
