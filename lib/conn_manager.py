from lib.chat_room import ChatRoom
from lib.nulluser import NullUser


class ContextManager:
    def __init__(self):
        self.active_connections: list[NullUser] = []
        self.__rooms: list[ChatRoom] = []

    async def connect(self, user: NullUser):
        await user.connection.accept()
        self.active_connections.append(user)

    async def disconnect(self, user: NullUser):
        await self.broadcast(f"Client '{user.username}' Disconnected")
        self.active_connections.remove(user)

    async def broadcast(self, data):
        _ = [await conn.connection.send_text(data) for conn in self.active_connections]

    def find_user(self, username: str) -> NullUser | None:
        for conn in self.active_connections:
            if conn.username == username:
                return conn
        return None

    def search_room(self, name) -> ChatRoom | None:
        found = [room for room in  self.__rooms if room.name == name]
        if found:
            return found[0]
        return None

    def add_room(self, room: ChatRoom) -> None:
        self.__rooms.append(room)


