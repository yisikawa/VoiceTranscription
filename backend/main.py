from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import shutil
import uuid
import logging
import asyncio
from typing import List

from config import UPLOAD_DIR

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Voice Transcription Studio API")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory task status storage (for simplicity)
# In production, use a database or Redis.
tasks = {}

@app.post("/upload")
async def upload_file(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """
    Upload a file and start the transcription process in the background.
    Returns a task_id immediately.
    """
    task_id = str(uuid.uuid4())
    tasks[task_id] = {"status": "processing", "progress": 0}
    
    background_tasks.add_task(process_upload, task_id, file)
    
    return {"task_id": task_id, "status": "processing"}

async def process_upload(task_id: str, file: UploadFile):
    """
    Background task wrapper for service logic.
    """
    try:
        # Create temp file to pass to service
        task_dir = UPLOAD_DIR / task_id
        task_dir.mkdir(parents=True, exist_ok=True)
        temp_file_path = task_dir / file.filename
        
        with open(temp_file_path, "wb") as buffer:
             shutil.copyfileobj(file.file, buffer)
             
        # Call service logic (synchronous for now within async wrapper)
        # Note: Heavy processing should ideally be in a separate process/worker
        from services import handle_task_sync
        result = await asyncio.to_thread(handle_task_sync, task_id, temp_file_path, task_dir)
        
        tasks[task_id] = {
            "status": "completed", 
            "result": result
        }
            
    except Exception as e:
        logger.error(f"Task {task_id} failed: {e}")
        tasks[task_id] = {"status": "failed", "error": str(e)}

@app.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """Check the status of a transcription task."""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks[task_id]

@app.get("/audio/{task_id}/{filename}")
async def get_audio_file(task_id: str, filename: str):
    """Serve audio files (original, vocals, etc.)"""
    file_path = UPLOAD_DIR / task_id / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)

@app.post("/save/{task_id}")
async def save_transcription(task_id: str, segments: List[dict]): # Simplified schema
    """Save corrected transcription."""
    task_dir = UPLOAD_DIR / task_id
    if not task_dir.exists():
        raise HTTPException(status_code=404, detail="Task not found")
        
    result_json_path = task_dir / "transcription_corrected.json"
    import json
    with open(result_json_path, "w", encoding="utf-8") as f:
        json.dump(segments, f, ensure_ascii=False, indent=2)
        
    return {"status": "saved"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
