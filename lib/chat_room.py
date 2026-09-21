import uuid

from lib.nulluser import NullUser
from lib.util import VisibilityPolicy


class ChatRoom:
    def __init__(self, name: str, max_clients: int, host: NullUser, visibility: VisibilityPolicy):
        self.name = name
        self.max_clients = max_clients
        self.host = host
        self.visibility = visibility
        self.room_id = str(uuid.uuid4())
        self.users: list[NullUser] = []

    @property
    def to_dict(self):
        return {
            "name": self.name,
            "maxClients": self.max_clients,
            "host": self.host.username,
            "visibility": self.visibility.name,
            "roomId": self.room_id,
            "users": [
                {
                    "username": user.username,
                    "isHost": user.id == self.host.id,
                    "color": user.color,
                    "user_id": user.id
                } for user in self.users
            ]
        }

    def join_user(self, user: NullUser):
        if len(self.users) < self.max_clients:
            self.users = [x for x in self.users if x.username != user.username]
            self.users.append(user)
            user.room = self

    async def broadcast(self, message: dict, exclude: str | None = None):
        dead_users = []
        for user in self.users:
            if user.username == exclude:
                continue
            try:
                await user.connection.send_json(message)
            except Exception:
                dead_users.append(user)
        for user in dead_users:
            self.users.remove(user)
            user.room = None

    def leave(self, user: NullUser):
        try:
            self.users.remove(user)
            user.room = None
        except ValueError:
            user.room = None

