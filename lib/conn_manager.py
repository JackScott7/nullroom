from fastapi import WebSocket


class NullUser:
    def __init__(self, username: str, ws_connection: WebSocket):
        self.username: str = username
        self.connection: WebSocket = ws_connection


class ContextManager:
    def __init__(self):
        self.active_connections: list[NullUser] = []

    async def connect(self, user: NullUser):
        await user.connection.accept()
        # await ws.accept()
        self.active_connections.append(user)

    async def disconnect(self, user: NullUser):
        await self.broadcast(f"Client '{user.username}' Disconnected")
        self.active_connections.remove(user)

    async def broadcast(self, data):
        _ = [await conn.connection.send_text(data) for conn in self.active_connections]

    def is_user_available(self, username: str) -> bool:
        for user in self.active_connections:
            if user.username == username:
                return False
        return True

