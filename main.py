from datetime import datetime, timezone

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from lib.chat_room import ChatRoom
from lib.conn_manager import ContextManager
from lib.message_protocol import MessageProtocol
from lib.nulluser import NullUser
from lib.util import VisibilityPolicy

nullroom = FastAPI(title="Nullroom")
origins = [
    "http://127.0.0.1",
    "http://127.0.0.1:5173",
    "http://localhost",
    "http://localhost:5173"
]
nullroom.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
ws_manager = ContextManager()


async def handle_join_room(payload: dict):
    data = payload["data"]
    username = payload["username"]
    ws = payload["ws"]

    room_id = data.get("room_id")
    room = ws_manager.search_room(room_id)
    user = ws_manager.find_user(username)

    if user is None:
        return

    if color := data.get("color"):
        user.color = color

    if not room:
        await ws.send_json({
            "type": MessageProtocol.ROOM_NOT_FOUND.value,
        })
        return

    if len(room.users) >= room.max_clients:
        await ws.send_json({
            "type": MessageProtocol.ROOM_FULL.value,
        })
        return

    if user not in room.users:
        room.join_user(user)

    await ws.send_json({
        "type": MessageProtocol.ROOM_JOINED.value,
        "room": room.to_dict
    })

    await room.broadcast({
        "type": MessageProtocol.USER_JOINED.value,
        "username": username,
        "user_id": user.id,
        "color": user.color,
        "room_users": room.to_dict["users"]
    }, exclude=username)

    await ws_manager.broadcast_all({
        "type": MessageProtocol.NEW_ROOM_AVAILABLE.value,
        "room": room.to_dict
    }, exclude=username)


async def handle_leave_room(payload: dict):
    data = payload["data"]
    username = data.get("username")
    room_id = data.get("roomId")

    user = ws_manager.find_user(username)
    if user is None:
        return

    room = ws_manager.search_room(room_id)
    if not room:
        return

    if room.host.username == username and user.is_host:
        # if host leaves the room, dc all users and redirect them to /rooms
        _ = [room.leave(x) for x in room.users]
        # prevent a case where previous host will be the next host of a room that they join
        user.is_host = False
        ws_manager.remove_room(room)
        await room.broadcast({
            "type": MessageProtocol.ROOM_CLOSED.value,
            "message": "Host has left the room"
        })
    else:
        room.leave(user)

        if len(room.users) < 1:
            await room.broadcast({
                "type": MessageProtocol.ROOM_CLOSED.value,
                "message": "You are not the host"
            })
            ws_manager.remove_room(room)
            return

        await room.broadcast({
            "type": MessageProtocol.USER_LEFT.value,
            "username": username,
            "user_id": user.id,
            "color": user.color,
            "room_space": len(room.users)
        }, exclude=None)


async def handle_set_username_color(payload: dict):
    username = payload["username"]
    data = payload["data"]
    ws = payload["ws"]
    user = ws_manager.find_user(username)
    if user:
        user.color = data.get("color")
        await ws.send_json({"success": True})


async def get_all_public_rooms(payload: dict):
    public_rooms = ws_manager.get_all_public_rooms()
    ws = payload["ws"]
    await ws.send_json({
        "type": MessageProtocol.PUBLIC_ROOMS.value,
        "data": [x.to_dict for x in public_rooms]
    })


async def handle_room_creation(payload):
    data = payload["data"]
    ws = payload["ws"]

    user = ws_manager.find_user(data.get("user"))

    if user is None:
        return

    room = ChatRoom(
        data.get("name"),
        data.get("maxClients"),
        user,
        visibility=VisibilityPolicy.public if data.get("visibility") == 'public' else VisibilityPolicy.private
    )
    user.is_host = True
    # room.host = user
    ws_manager.add_room(room)
    room.join_user(user)

    await ws.send_json({
        "type": MessageProtocol.ROOM_CREATED.value,
        "room": room.to_dict
    })

    # if this room is PUBLIC, Broadcast it to all users that don't have a room
    if room.visibility == VisibilityPolicy.public:
        await ws_manager.broadcast_all({
            "type": MessageProtocol.NEW_ROOM_AVAILABLE.value,
            "room": room.to_dict
        }, exclude=user.username)


async def broadcast_message_to_room(payload):
    data = payload["data"]
    message_text = data.get("message")
    sender_name = data.get("sender")
    room_id = data.get("roomId")
    temp_id = data.get("tempId")
    room = ws_manager.search_room(room_id)
    if not room:
        return

    sender_user = ws_manager.find_user(sender_name)
    color = sender_user.color if sender_user else "#ffffff"
    broadcast_payload = {
        "type": MessageProtocol.MESSAGE_SENT.value,
        "text": message_text,
        "sender": sender_name,
        "color": color,
        "time": datetime.now(tz=timezone.utc).strftime("%H:%M:%S"),
        "tempId": temp_id
    }

    await room.broadcast(broadcast_payload, exclude=None)


async def get_online_users_count(payload):
    ws = payload["ws"]
    user_count = ws_manager.get_online_user_count()
    await ws.send_json({
        "type": MessageProtocol.USER_COUNT.value,
        "online_users": user_count
    })


async def authenticate_user(payload):
    ws = payload["ws"]
    data = payload["data"]
    username = payload["username"]

    auth = data.get('username') == username

    await ws.send_json({
        'type': MessageProtocol.AUTHENTICATION.value,
        'authenticated': auth
    })

    if not auth:
        await ws_manager.disconnect(NullUser(username, ws))


async def logout_current_user(payload):
    ws = payload["ws"]
    username = payload["username"]



@nullroom.websocket("/api/ws/{username}")
async def websocket_endpoint(ws: WebSocket, username: str):
    existing = ws_manager.find_user(username)
    if existing:
        if existing.room:
            existing.room.leave(existing)
        ws_manager.active_connections.remove(existing)

    user = NullUser(username, ws)
    await ws_manager.connect(user)
    try:
        while True:
            data = await ws.receive_json()
            message_type = MessageProtocol(data.get("type"))
            payload = {
                "ws": ws,
                "username": username,
                "data": data
            }
            match message_type:
                case message_type.JOIN_ROOM:
                    await handle_join_room(payload)
                case message_type.LEAVE_ROOM:
                    await handle_leave_room(payload)
                case message_type.SET_COLOR:
                    await handle_set_username_color(payload)
                case message_type.GET_PUBLIC_ROOMS:
                    await get_all_public_rooms(payload)
                case message_type.CREATE_ROOM:
                    await handle_room_creation(payload)
                case message_type.SEND_CHAT_MESSAGE:
                    await broadcast_message_to_room(payload)
                case message_type.GET_ONLINE_USERS_COUNT:
                    await get_online_users_count(payload)
                case message_type.AUTHENTICATE_USER:
                    await authenticate_user(payload)
                case message_type.LOGOUT_CURRENT_USER:
                    await ws_manager.disconnect(user)
    except WebSocketDisconnect:
        if user.room:
            user.room.leave(user)
            await user.room.broadcast({
                "type": MessageProtocol.USER_LEFT.value,
                "username": username,
                "user_id": user.id
            }, exclude=username)
        await ws_manager.disconnect(user)


@nullroom.post("/api/is-user-available")
async def is_user_available(request: Request):
    if not await request.body():
        return JSONResponse(status_code=400, content={"status": "error_no_body"})

    data = await request.json()
    if not data:
        return JSONResponse(status_code=400, content={"status": "error"})

    username = data.get("username", None).strip()

    if not username:
        return JSONResponse(status_code=400, content={"status": "error_empty_username"})

    taken = ws_manager.find_user(username)
    if taken:
        return JSONResponse(status_code=409, content={"status": "taken"})

    return JSONResponse(status_code=200, content={"status": "available"})


@nullroom.get("/api/conns")
def get_conns():
    return JSONResponse(status_code=200, content={
        "users": [
            {"name": x.username, "color": x.color} for x in ws_manager.active_connections
        ]
    })
