from lib.chat_room import ChatRoom
from lib.nulluser import NullUser
from lib.util import VisibilityPolicy


class ContextManager:
    def __init__(self):
        self.active_connections: list[NullUser] = []
        self.__rooms: list[ChatRoom] = []

    async def connect(self, user: NullUser):
        await user.connection.accept()
        self.active_connections.append(user)

    async def disconnect(self, user: NullUser):
        if user in self.active_connections:
            self.active_connections.remove(user)

        try:
            await user.connection.close()
        except Exception:
            pass

    async def broadcast_all(self, data: dict, exclude: str | None = None):
        dead = []
        for conn in self.active_connections:
            if conn.room is None:
                try:
                    if conn.username == exclude:
                        continue
                    await conn.connection.send_json(data)
                except Exception:
                    pass
        for conn in dead:
            if conn in self.active_connections:
                self.active_connections.remove(conn)

    def find_user(self, username: str) -> NullUser | None:
        for conn in self.active_connections:
            if conn.username == username:
                return conn
        return None

    def search_room(self, room_id) -> ChatRoom | None:
        found = [room for room in  self.__rooms if room.room_id == room_id]
        if found:
            return found[0]
        return None

    def add_room(self, room: ChatRoom) -> None:
        self.__rooms.append(room)

    def get_all_public_rooms(self) -> list[ChatRoom]:
        return [x for x in self.__rooms if x.visibility == VisibilityPolicy.public]

    def remove_room(self, room: ChatRoom) -> None:
        self.__rooms.remove(room)

    def get_online_user_count(self) -> int:
        return len(self.active_connections)

