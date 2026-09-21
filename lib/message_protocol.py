from enum import StrEnum


class MessageProtocol(StrEnum):
    SET_COLOR = "set_color"

    USER_LEFT = "user_left"
    USER_JOINED = "user_joined"
    USER_COUNT = "user_count"
    AUTHENTICATE_USER = "authenticate_user"
    AUTHENTICATION = "authentication"
    LOGOUT_CURRENT_USER = "logout_current_user"

    JOIN_ROOM = "join_room"
    CREATE_ROOM = "create_room"

    ROOM_JOINED = "room_joined"
    ROOM_CREATED = "room_created"
    ROOM_FULL = "room_full"
    ROOM_CLOSED = "room_closed"
    LEAVE_ROOM = "leave_room"

    GET_PUBLIC_ROOMS = "get_public_rooms"
    PUBLIC_ROOMS = "public_rooms"
    ROOM_NOT_FOUND = "room_not_found"
    NEW_ROOM_AVAILABLE = "new_room_available"

    SEND_CHAT_MESSAGE = "send_chat_message"
    MESSAGE_SENT = "message_sent"

    GET_ONLINE_USERS_COUNT = "get_online_users_count"
