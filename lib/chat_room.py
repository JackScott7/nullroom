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

    @property
    def to_dict(self):
        return {
            "name": self.name,
            "maxClients": self.max_clients,
            "host": self.host.username,
            "visibility": self.visibility.name
        }

    def join(self, client: NullUser):
        ...
