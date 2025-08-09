from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import FileResponse
from .models import IdeaRequest, ChatMessage, ChatEvent
from .tasks import start_task, get_task
from .script_gen import generate_script_and_scenes
from . import config
import asyncio

app = FastAPI(title="Chat-to-Reel Generator")

@app.post("/idea")
def submit_idea(req: IdeaRequest):
    task_id = start_task(req.idea)
    return {"task_id": task_id}

@app.get("/result/{task_id}")
def get_result(task_id: str):
    record = get_task(task_id)
    if not record:
        raise HTTPException(status_code=404, detail="Task not found")
    return record.to_public()

@app.get("/download/{task_id}")
def download(task_id: str):
    record = get_task(task_id)
    if not record or not record.video_path:
        raise HTTPException(status_code=404, detail="Video not ready")
    return FileResponse(record.video_path, media_type='video/mp4', filename=f"reel_{task_id}.mp4")

@app.websocket("/ws/chat")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            raw = await ws.receive_json()
            msg = ChatMessage(**raw)
            if msg.role == 'user' and 'idea:' in msg.content.lower():
                idea = msg.content.split(':',1)[1].strip()
                await ws.send_json(ChatEvent(type='ack', data={'message': 'Processing idea'}).dict())
                # Synchronous generation (stream style)
                script_result = generate_script_and_scenes(idea)
                await ws.send_json(ChatEvent(type='script_draft', data={'script': script_result.script}).dict())
                await ws.send_json(ChatEvent(type='scenes', data={'scenes': [s.dict() for s in script_result.scenes]}).dict())
                # Kick off background video build
                task_id = start_task(idea)
                await ws.send_json(ChatEvent(type='task_started', data={'task_id': task_id}).dict())
            else:
                await ws.send_json(ChatEvent(type='info', data={'message': 'Send an idea with prefix "Idea:"'}).dict())
    except WebSocketDisconnect:
        pass
