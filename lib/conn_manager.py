from fastapi import WebSocket


class ContextManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active_connections.append(ws)

    async def disconnect(self, ws: WebSocket, client_id: str):
        await self.broadcast(ws, f"Client '{client_id}' Disconnected")
        self.active_connections.remove(ws)

    async def broadcast(self, ws: WebSocket, data):
        _ = [await ws.send_text(data) for ws in self.active_connections]



