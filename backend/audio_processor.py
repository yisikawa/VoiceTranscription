import os
import shutil
import subprocess
from pathlib import Path
import soundfile as sf
import torch
from demucs.apply import apply_model
from demucs.audio import AudioFile
from demucs.pretrained import get_model
from faster_whisper import WhisperModel
from config import DEMUCS_MODEL_NAME, WHISPER_MODEL_NAME, WHISPER_SETTINGS, setup_ffmpeg

# Initialize FFmpeg
setup_ffmpeg()

# --- Whisper Model Management ---
class _WhisperModelManager:
    _instance = None
    _model = None
    _model_name = None

    @classmethod
    def get_model(cls, model_name: str):
        if cls._model is None or cls._model_name != model_name:
            device = "cuda" if torch.cuda.is_available() else "cpu"
            compute_type = "float16" if device == "cuda" else "int8"
            
            print(f"--- Loading faster-whisper model ({model_name}) on {device} ({compute_type}) ---")
            try:
                cls._model = WhisperModel(model_name, device=device, compute_type=compute_type)
                cls._model_name = model_name
            except Exception as e:
                print(f"Failed to load model on {device}: {e}. Falling back to CPU...")
                cls._model = WhisperModel(model_name, device="cpu", compute_type="int8")
                cls._model_name = model_name
        return cls._model

# --- Audio Extraction ---
def extract_audio(input_path: Path, output_path: Path) -> bool:
    """Extract audio from video file using FFmpeg via ffmpeg-python or subprocess."""
    try:
        import ffmpeg
        import shutil
        import imageio_ffmpeg
        
        # Determine FFmpeg executable
        ffmpeg_exe = shutil.which("ffmpeg")
        if not ffmpeg_exe:
             ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
             
        print(f"Using FFmpeg executable: {ffmpeg_exe}")
        
        if input_path.suffix.lower() in {".wav", ".mp3", ".flac", ".m4a"}:
            # Already audio, just copy or convert if needed
            # For consistency, convert to WAV
            (
                ffmpeg
                .input(str(input_path))
                .output(str(output_path), ac=1, ar=16000) # Mono 16kHz for Whisper
                .run(cmd=ffmpeg_exe, overwrite_output=True, capture_stdout=True, capture_stderr=True)
            )
            return True
        
        # Video file
        (
            ffmpeg
            .input(str(input_path))
            .output(str(output_path), ac=1, ar=16000) # Extract audio track
            .run(cmd=ffmpeg_exe, overwrite_output=True, capture_stdout=True, capture_stderr=True)
        )
        return True
    except Exception as e:
        print(f"Error extracting audio: {e}")
        return False

# --- Vocal Separation (Demucs) ---
def separate_vocals(audio_path: Path, output_dir: Path) -> Path:
    """
    Separate vocals using Demucs. Returns path to vocals file.
    """
    try:
        print(f"Loading Demucs model ({DEMUCS_MODEL_NAME})...")
        model = get_model(DEMUCS_MODEL_NAME)
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model.to(device)

        # Load audio using Demucs AudioFile (wrapping ffmpeg)
        wav = AudioFile(audio_path).read(
            streams=0,
            samplerate=model.samplerate,
            channels=model.audio_channels
        )
        
        # Normalize
        ref = wav.mean(0)
        wav = (wav - ref.mean()) / ref.std()
        
        print("Starting separation...")
        # Add batch dimension and apply
        sources = apply_model(model, wav[None], device=device, shifts=1, split=True, overlap=0.25, progress=True)[0]
        
        # Denormalize
        sources = sources * ref.std() + ref.mean()

        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Get vocals index
        vocals_idx = model.sources.index('vocals')
        vocals = sources[vocals_idx]
        
        # Save vocals
        vocals_np = vocals.cpu().numpy().T
        filename_stem = audio_path.stem
        vocals_path = output_dir / f"{filename_stem}_vocals.wav"
        
        print(f"Saving vocals to {vocals_path}")
        sf.write(str(vocals_path), vocals_np, model.samplerate)
        
        return vocals_path

    except Exception as e:
        print(f"Error separating vocals: {e}")
        import traceback
        traceback.print_exc()
        return None

# --- Transcription (Whisper) ---
def transcribe_audio(audio_path: Path):
    """
    Transcribe audio using faster-whisper.
    Returns list of segments with start, end, text.
    """
    try:
        print(f"--- Start Transcription: {audio_path.name} ---")
        model = _WhisperModelManager.get_model(WHISPER_MODEL_NAME)

        segments_generator, info = model.transcribe(
            str(audio_path),
            **WHISPER_SETTINGS
        )
        
        print(f"Detected language: {info.language} ({info.language_probability:.2f})")
        
        results = []
        for segment in segments_generator:
            text = segment.text.strip()
            if not text:
                continue
            
            seg_data = {
                "id": segment.id,
                "start": round(segment.start, 2),
                "end": round(segment.end, 2),
                "text": text
            }
            results.append(seg_data)
            print(f"[{segment.start:.2f} -> {segment.end:.2f}] {text}")
            
        return {"language": info.language, "segments": results}

    except Exception as e:
        print(f"Error transcribing: {e}")
        return None
