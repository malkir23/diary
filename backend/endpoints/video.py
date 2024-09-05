from fastapi import APIRouter, WebSocket, Request, WebSocketDisconnect, Response, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.templating import Jinja2Templates
from typing import List
from starlette.requests import Request
from pathlib import Path

templates = Jinja2Templates(directory="backend/templates/")

router = APIRouter()
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()
video_directory = "backend/static/video"


@router.get("/video_page")
async def movies(request: Request):
    return templates.TemplateResponse("video.html", {"request": request})

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            print(data)
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{client_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")

@router.get("/movie/{video_filename}")
async def stream_video(video_filename: str = "sample-5s.mp4",  start_seconds: int = 0):
    video_path = Path(video_directory) / video_filename

    # Check if the video file exists
    if not video_path.is_file():
        raise HTTPException(status_code=404, detail="Video not found")

    # Calculate the start byte based on the desired start time (in seconds)
    start_byte = int(start_seconds * 1024 * 1024)  # Assuming 1 MB/s bitrate

    # Open the video file for streaming
    video_file = open(video_path, "rb")
    video_file.seek(start_byte)

    # Function to generate video content in chunks
    async def stream_generator():
        chunk_size = 1024 * 1024  # 1 MB chunks, adjust as needed
        while True:
            chunk = video_file.read(chunk_size)
            if not chunk:
                break
            yield chunk

    # Set the content type to "video/mp4" and return a StreamingResponse
    return StreamingResponse(
        stream_generator(),
        media_type="video/mp4",
        headers={
            "Content-Range": f"bytes {start_byte}-",
            "Accept-Ranges": "bytes",
        },
    )
