import os
from pathlib import Path

# Base Path
BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"

# Create directories if they don't exist
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Audio Settings
ALLOWED_EXTENSIONS = {".mp3", ".wav", ".m4a", ".mp4", ".mov", ".flac"}
DEMUCS_MODEL_NAME = "htdemucs"  # Optimized model for speed/quality balance
WHISPER_MODEL_NAME = "base" # Using base for faster testing (was large-v3)
WHISPER_SETTINGS = {
    "beam_size": 5,
    "vad_filter": True,
    "vad_parameters": dict(min_silence_duration_ms=500),
}

# FFmpeg Path Handling
def setup_ffmpeg():
    """Ensure ffmpeg is in path using imageio_ffmpeg."""
    try:
        import imageio_ffmpeg
        ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
        ffmpeg_dir = str(Path(ffmpeg_path).parent)
        
        # Add to PATH if not present
        if ffmpeg_dir not in os.environ["PATH"]:
            print(f"Adding FFmpeg to PATH: {ffmpeg_dir}")
            os.environ["PATH"] += os.pathsep + ffmpeg_dir
    except ImportError:
        print("imageio_ffmpeg not found. Ensure FFmpeg is installed and in PATH.")
