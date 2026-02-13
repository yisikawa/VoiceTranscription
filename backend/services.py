from pathlib import Path
import logging
import json
import shutil
import uuid
from typing import Dict, Any

from audio_processor import extract_audio, separate_vocals, transcribe_audio
from config import UPLOAD_DIR, ALLOWED_EXTENSIONS

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def handle_task_sync(task_id: str, file_path: Path, task_dir: Path) -> Dict[str, Any]:
    """
    Synchronous processing function called by the background worker.
    Args:
        task_id: Unique ID for the task.
        file_path: Path to the uploaded file.
        task_dir: Directory for task artifacts.
    Returns:
        Dictionary with processing results.
    """
    try:
        logger.info(f"Starting processing for task {task_id}")
        
        # 1. Extract Audio
        extracted_audio_path = task_dir / "extracted_audio.wav"
        if not extract_audio(file_path, extracted_audio_path):
            raise Exception("Failed to extract audio from uploaded file.")
        
        logger.info(f"Audio extracted to {extracted_audio_path}")
        
        # 2. Separate Vocals (Optional but recommended for transcription accuracy)
        # Note: Demucs can take time, so this is why it's a background task.
        vocals_path = separate_vocals(extracted_audio_path, task_dir)
        
        if not vocals_path:
             logger.warning("Vocal separation failed or yielded no output, falling back to original audio.")
             vocals_path = extracted_audio_path
        else:
             logger.info(f"Vocals separated to {vocals_path}")

        # 3. Transcribe
        transcription_result = transcribe_audio(vocals_path)
        
        if not transcription_result:
             raise Exception("Transcription failed.")
             
        logger.info(f"Transcription completed for task {task_id}")

        # 4. Save initial transcription
        result_json_path = task_dir / "transcription.json"
        with open(result_json_path, "w", encoding="utf-8") as f:
            json.dump(transcription_result, f, ensure_ascii=False, indent=2)
            
        return {
            "task_id": task_id,
            "original_filename": file_path.name,
            "extracted_audio": extracted_audio_path.name,
            "vocals_audio": vocals_path.name,
            "transcription": transcription_result
        }

    except Exception as e:
        logger.error(f"Error in handle_task_sync for task {task_id}: {e}")
        raise e
