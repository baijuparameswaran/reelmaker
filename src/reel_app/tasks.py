import threading
from pathlib import Path
from typing import Dict
from .models import InternalTaskRecord
from . import config
from .script_gen import generate_script_and_scenes
from .video import build_video

_tasks: Dict[str, InternalTaskRecord] = {}
_lock = threading.Lock()

def start_task(idea: str) -> str:
    record = InternalTaskRecord(idea=idea)
    with _lock:
        _tasks[record.task_id] = record
    thread = threading.Thread(target=_run_task, args=(record.task_id,), daemon=True)
    thread.start()
    return record.task_id


def get_task(task_id: str) -> InternalTaskRecord | None:
    return _tasks.get(task_id)


def _run_task(task_id: str):
    record = get_task(task_id)
    if not record:
        return
    record.status = "generating_script"
    try:
        script_result = generate_script_and_scenes(record.idea)
        record.scenes = script_result.scenes
        record.status = "building_video"
        out_path = config.OUTPUT_DIR / f"{record.task_id}.mp4"
        build_video(record.scenes, out_path)
        record.video_path = str(out_path)
        record.status = "completed"
    except Exception as e:
        record.status = "failed"
        record.message = str(e)
