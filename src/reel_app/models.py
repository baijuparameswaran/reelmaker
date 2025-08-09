from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime

class IdeaRequest(BaseModel):
    idea: str

class Scene(BaseModel):
    index: int
    text: str
    duration: float

class TaskStatus(BaseModel):
    task_id: str
    status: str
    message: Optional[str] = None
    video_path: Optional[str] = None
    scenes: Optional[List[Scene]] = None

class ChatMessage(BaseModel):
    role: str  # 'user' | 'assistant' | 'system'
    content: str

class ChatEvent(BaseModel):
    type: str
    data: dict

class ScriptResult(BaseModel):
    script: str
    scenes: List[Scene]

def new_task_id() -> str:
    return uuid.uuid4().hex

class InternalTaskRecord:
    def __init__(self, idea: str):
        self.task_id = new_task_id()
        self.idea = idea
        self.status = "pending"
        self.message = None
        self.video_path = None
        self.created_at = datetime.utcnow()
        self.updated_at = self.created_at
        self.scenes: List[Scene] = []

    def to_public(self) -> TaskStatus:
        return TaskStatus(
            task_id=self.task_id,
            status=self.status,
            message=self.message,
            video_path=self.video_path,
            scenes=self.scenes or None,
        )
