from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from lib.conn_manager import ContextManager, NullUser


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


@app.post("/api/userAvailable")
async def is_user_available(request: Request):
    if not await request.body():
        return JSONResponse(status_code=400, content={"status": "error_no_body"})

    data = await request.json()
    if not data:
        return JSONResponse(status_code=400, content={"status": "error"})

    username = data.get("username", None).strip()

    if not username:
        return JSONResponse(status_code=400, content={"status": "error_empty_username"})

    is_available = ws_manager.is_user_available(username)
    if is_available:
        return JSONResponse(status_code=200, content={"status": "available"})
    else:
        return JSONResponse(status_code=409, content={"status": "taken"})


@app.get("/api/conns")
def get_conns():
    return JSONResponse(status_code=200, content={"no_connections": len(ws_manager.active_connections)})



