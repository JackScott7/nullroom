from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from lib.chat_room import ChatRoom
from lib.conn_manager import ContextManager
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


@app.websocket("/api/ws/{client_id}")
async def websocket_endpoint(ws: WebSocket, client_id: str):
    user = NullUser(client_id, ws)
    await ws_manager.connect(user)
    try:
        while True:
            data = await ws.receive_text()
            await ws_manager.broadcast(data)
    except WebSocketDisconnect:
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
    print(ws_manager.active_connections)
    return JSONResponse(status_code=200, content={"no_connections": len(ws_manager.active_connections)})


@app.post("/api/create-room")
async def create_room(request: Request):
    data = await request.json()

    room = ChatRoom(
        data.get("name"),
        data.get("maxClients"),
        ws_manager.find_user(data.get("user")),
        visibility=VisibilityPolicy.PUBLIC if data.get("visibility") == 'public' else VisibilityPolicy.PRIVATE
    )

    ws_manager.add_room(room)

    return JSONResponse(status_code=201, content={"status": "created", "room": room.to_dict})


@app.get("/api/rooms/{room_name}")
async def get_room(room_name: str):
    room = ws_manager.search_room(room_name)
    if room:
        return JSONResponse(status_code=200, content={"success": True, "data": room.to_dict})
    else:
        return JSONResponse(status_code=404, content={"success": False})

