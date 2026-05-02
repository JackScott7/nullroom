from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from lib.chat_room import ChatRoom
from lib.conn_manager import ContextManager
from lib.message_protocol import MessageProtocol
from lib.nulluser import NullUser
from lib.util import VisibilityPolicy


app = FastAPI(title="Nullroom")
origins = [
    "http://localhost",
    "http://localhost:5173"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"]
)
ws_manager = ContextManager()


async def handle_join_room(payload: dict):
    data = payload["data"]
    username = payload["username"]
    ws = payload["ws"]

    room_id = data.get("room_id")
    room = ws_manager.search_room(room_id)
    user = ws_manager.find_user(username)
    if room:
        await ws.send_json({
            "type": "room_joined",
            "room": room.to_dict
        })
        room.join_user(user)
        await room.broadcast({
            "type": "user_joined",
            "username": username,
            "color": user.color
        }, user.username)
        return
    await ws.send_json({
        "type": MessageProtocol.ROOM_NOT_FOUND.name,
    })


async def handle_leave_room(payload: dict):
    data = payload["data"]
    username = data["username"]
    room_id = data["roomId"]

    user = ws_manager.find_user(username)

    room = ws_manager.search_room(room_id)
    room.leave(user)
    await room.broadcast({
        "type": "user_left",
        "username": username,
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
        "type": "public_rooms",
        "data": [x.to_dict for x in public_rooms]
    })


async def handle_room_creation(payload):
    data = payload["data"]
    ws = payload["ws"]

    user = ws_manager.find_user(data.get("user"))
    room = ChatRoom(
        data.get("name"),
        data.get("maxClients"),
        user,
        visibility=VisibilityPolicy.public if data.get("visibility") == 'public' else VisibilityPolicy.private
    )
    user.is_host = True
    ws_manager.add_room(room)
    room.join_user(user)

    await ws.send_json({
        "type": "room_created",
        "room": room.to_dict
    })

    # if this room is PUBLIC, Broadcast it to all users that don't have a room
    if room.visibility == VisibilityPolicy.public:
        await ws_manager.broadcast_all({
            "type": "new_room_available",
            "room": room.to_dict
        })


async def broadcast_message_to_room(payload):
    data = payload["data"]
    message_text = data.get("message")
    sender_name = data.get("sender")
    room_id = data.get("roomId")

    room = ws_manager.search_room(room_id)
    if not room:
        return

    sender_user = ws_manager.find_user(sender_name)
    color = sender_user.color if sender_user else "#ffffff"

    broadcast_payload = {
        "type": "message_sent",
        "text": message_text,
        "sender": sender_name,
        "color": color,
        "time": datetime.now().isoformat(),
    }

    await room.broadcast(broadcast_payload, exclude=None)



@app.websocket("/api/ws/{username}")
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


    except WebSocketDisconnect:
        if user.room:
            user.room.leave(user)
            await user.room.broadcast({
                "type": "user_left",
                "username": username,
            }, exclude=username)
        await ws_manager.disconnect(user)


@app.post("/api/is-user-available")
async def is_user_available(request: Request):
    if not await request.body():
        return JSONResponse(status_code=400, content={"status": "error_no_body"})

    data = await request.json()
    if not data:
        return JSONResponse(status_code=400, content={"status": "error"})

    username = data.get("username", None).strip()

    if not username:
        return JSONResponse(status_code=400, content={"status": "error_empty_username"})

    is_available = ws_manager.find_user(username)
    if not is_available:
        return JSONResponse(status_code=200, content={"status": "available"})
    else:
        return JSONResponse(status_code=409, content={"status": "taken"})


@app.get("/api/conns")
def get_conns():
    return JSONResponse(status_code=200, content={
        "users": [
            {"name": x.username, "color": x.color} for x in ws_manager.active_connections
        ]
    })
