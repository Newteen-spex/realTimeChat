from fastapi import FastAPI, WebSocket, Request, Form
from starlette.websockets import WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from typing import List
import random
import json

app = FastAPI()

# 静态文件目录，用于存放前端界面文件
templates = Jinja2Templates(directory="templates")

# 用于存储连接的客户端
connected_clients: List[WebSocket] = []

#用于存储昵称的字典
name_list = {}

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await websocket.accept()
    connected_clients.append(websocket)

    try:
        while True:
            message = await websocket.receive_text()
            data = {
                "message": f"【{name_list[client_id]}】: {message}"
                # "online": len(connected_clients)
            }
            #将字典转换为JSON格式的字符串
            json_data = json.dumps(data)

            await broadcast_message(json_data)

    except WebSocketDisconnect:
        connected_clients.remove(websocket)
        await broadcast_message(f"Client {client_id} left the chat.")


@app.get("/")
async def form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/submit")
async def submit(request: Request, username: str = Form(...)):
    randNu = random.randint(1, 100)
    name_list[randNu] = username
    return templates.TemplateResponse("index.html",
    {
        "request": request, 
        "username": username,
        "number": randNu
        # "online": len(connected_clients)
    })

async def broadcast_message(message: str):
    for client in connected_clients:
        await client.send_text(message)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
