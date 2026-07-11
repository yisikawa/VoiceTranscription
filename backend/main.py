from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from pydantic import BaseModel
import json
import logging
import asyncio
import shutil
import uuid
from typing import List, Union

from config import UPLOAD_DIR, ALLOWED_EXTENSIONS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Voice Transcription Studio API")

MAX_UPLOAD_SIZE = 200 * 1024 * 1024  # 200MB

app.add_middleware(
    CORSMiddleware,
    # フロントエンド(ポート5152)からのアクセスを localhost / プライベートIP で許可
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1|192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3}):5152",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

tasks = {}


class SegmentIn(BaseModel):
    id: Union[int, str]
    start: float
    end: float
    text: str


def get_task_dir(task_id: str) -> Path:
    """task_id が UUID 形式であることを検証し、タスクディレクトリを返す。"""
    try:
        uuid.UUID(task_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Task not found")
    return UPLOAD_DIR / task_id


@app.post("/upload")
async def upload_file(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    # ファイル名を安全な形に正規化
    safe_name = Path(file.filename).name
    suffix = Path(safe_name).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"対応していないファイル形式です: {suffix}")

    task_id = str(uuid.uuid4())
    task_dir = UPLOAD_DIR / task_id
    task_dir.mkdir(parents=True, exist_ok=True)
    temp_file_path = task_dir / safe_name

    # メモリに全量を載せず、チャンクで書き込みながらサイズ検査する
    size = 0
    try:
        with open(temp_file_path, "wb") as buffer:
            while chunk := await file.read(1024 * 1024):
                size += len(chunk)
                if size > MAX_UPLOAD_SIZE:
                    raise HTTPException(status_code=413, detail="ファイルサイズが200MBを超えています")
                buffer.write(chunk)
    except HTTPException:
        shutil.rmtree(task_dir, ignore_errors=True)
        raise

    tasks[task_id] = {"status": "processing", "progress": 0}
    background_tasks.add_task(process_task, task_id, temp_file_path, task_dir)

    return {"task_id": task_id, "status": "processing"}


async def process_task(task_id: str, file_path: Path, task_dir: Path):
    try:
        from services import handle_task_sync
        result = await asyncio.to_thread(handle_task_sync, task_id, file_path, task_dir)
        tasks[task_id] = {"status": "completed", "result": result}
    except Exception as e:
        logger.error(f"Task {task_id} failed: {e}")
        tasks[task_id] = {"status": "failed", "error": str(e)}


@app.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks[task_id]


@app.get("/audio/{task_id}/{filename}")
async def get_audio_file(task_id: str, filename: str):
    task_dir = get_task_dir(task_id)
    safe_name = Path(filename).name
    file_path = (task_dir / safe_name).resolve()
    # パストラバーサル対策: UPLOAD_DIR 配下であることを確認
    if not file_path.is_relative_to(UPLOAD_DIR.resolve()):
        raise HTTPException(status_code=404, detail="File not found")
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)


@app.post("/save/{task_id}")
async def save_transcription(task_id: str, segments: List[SegmentIn]):
    task_dir = get_task_dir(task_id)
    if not task_dir.exists():
        raise HTTPException(status_code=404, detail="Task not found")

    result_json_path = task_dir / "transcription_corrected.json"
    with open(result_json_path, "w", encoding="utf-8") as f:
        json.dump([s.model_dump() for s in segments], f, ensure_ascii=False, indent=2)

    return {"status": "saved"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
