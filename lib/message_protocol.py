from enum import StrEnum


class MessageProtocol(StrEnum):
    JOIN_ROOM = "join_room"
    CREATE_ROOM = "create_room"
    CHAT_MESSAGE = "chat_message"
    LEAVE_ROOM = "leave_room"
    ROOM_JOINED = "room_joined"
    ROOM_NOT_FOUND = "room_not_found"
    SET_COLOR = "set_color"
    GET_ROOMS = "get_rooms"

