from uuid import uuid4

from fastapi import WebSocket


class NullUser:
    def __init__(self, username: str, ws_connection: WebSocket, is_host: bool = False):
        self.username: str = username
        self.connection: WebSocket = ws_connection
        self.is_host: bool = is_host
        self.room = None
        self.__color: str | None = None
        self.__id = f"{self.username}-{uuid4()}"

    def __str__(self):
        return f"{self.username} {self.color}"

    @property
    def color(self):
        return self.__color

    @color.setter
    def color(self, value):
        self.__color = value

    @property
    def id(self):
        return self.__id
