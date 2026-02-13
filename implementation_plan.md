# Voice Transcription Studio - Implementation Plan

## Overview
A web-based tool for transcribing audio/video files, separating vocals, and providing a real-time editor to correct transcriptions while listening to the audio. Built using the `LyricSyncAI` stack as a reference.

## Technology Stack
- **Backend**: Python (FastAPI), Uvicorn
  - AI Models: `faster-whisper` (Transcription), `Demucs` (Vocal Separation)
  - Audio Processing: `ffmpeg-python`, `soundfile`, `librosa`
- **Frontend**: React (Vite), TypeScript
  - Styling: Tailwind CSS
  - Audio Visualization: `wavesurfer.js`
  - Icons: `lucide-react`

## Folder Structure
```
d:\AntiGravity\VoiceTranscription\
├── backend\
│   ├── main.py
│   ├── services.py
│   ├── audio_processor.py
│   ├── config.py
│   ├── requirements.txt
│   └── uploads\
├── frontend\
│   ├── src\
│   │   ├── components\
│   │   │   ├── AudioPlayer.tsx
│   │   │   ├── TranscriptionEditor.tsx
│   │   │   └── FileUpload.tsx
│   │   ├── hooks\
│   │   │   └── useAudio.ts
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── index.html
│   ├── tailwind.config.js
│   └── package.json
└── README.md
```

## Phase 1: Backend Setup & Core Logic (Python)
- [x] Initialize Python environment and `requirements.txt`.
- [x] Implement `audio_processor.py`:
    - Port `demucs` logic for vocal separation.
    - Port `faster-whisper` logic for timestamped transcription.
- [x] Create FastAPI endpoints in `main.py`:
    - `POST /upload`: Handle file upload, trigger separation & transcription.
    - `GET /audio/{filename}`: Serve audio files.
    - `POST /save`: Save corrected transcription.

## Phase 2: Frontend Setup (React + Vite)
- [x] Initialize React project with TypeScript & Vite.
- [x] Setup Tailwind CSS.
- [x] Create `FileUpload` component with drag-and-drop support.
- [x] Implement `AudioPlayer` using `wavesurfer.js` for waveform visualization.
- [x] Create `TranscriptionEditor`:
    - Display text segments with timestamps.
    - Highlight current segment during playback.
    - Allow text editing and seeking on click.

## Phase 3: Integration & Polish
- [x] Connect Frontend to Backend API.
- [ ] Implement keyboard shortcuts (e.g., Space to play/pause, Ctrl+Enter to save).
- [ ] Design polish (Dark mode, smooth transitions).
- [ ] Export functionality (SRT, JSON, TXT).

## Phase 4: Testing & Optimization
- [ ] Verify large file handling.
- [ ] Optimize Whisper settings for Japanese.
- [ ] Ensure responsive UI.
