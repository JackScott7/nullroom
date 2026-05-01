from fastapi import WebSocket


class NullUser:
    def __init__(self, username: str, ws_connection: WebSocket):
        self.username: str = username
        self.connection: WebSocket = ws_connection

    def __str__(self):
        return self.username