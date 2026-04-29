import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse, JSONResponse
from lib.conn_manager import ContextManager, NullUser

app = FastAPI(title="Nullroom")
ws_manager = ContextManager()


@app.get("/")
async def root():
    with open(os.path.join(os.path.dirname(__file__), "templates", "index.html")) as f:
        return HTMLResponse(content=f.read(), status_code=200)


@app.websocket("/ws/{client_id}")
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
    data = await request.json()
    if not data:
        return JSONResponse(status_code=400, content={"message": "No data provided"})

    found = ws_manager.find_user(data.get('username', None))
    if not found:
        return JSONResponse(status_code=200, content={"status": "available"})
    else:
        return JSONResponse(status_code=409, content={"status": "taken"})


@app.get("/conns")
def get_conns():
    return JSONResponse(status_code=200, content={"no_connections": len(ws_manager.active_connections)})



