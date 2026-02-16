# Voice Transcription Studio - 実装プラン

## 概要
オーディオ/ビデオファイルの文字起こし、ボーカル分離、および音声を聴きながら文字起こしを修正できるリアルタイムエディタを提供するウェブベースのツール。`LyricSyncAI` スタックをリファレンスとして構築。

## 技術スタック
- **バックエンド**: Python (FastAPI), Uvicorn
  - AI モデル: `faster-whisper` (文字起こし), `Demucs` (ボーカル分離)
  - 音声処理: `ffmpeg-python`, `soundfile`, `librosa`
- **フロントエンド**: React (Vite), TypeScript
  - スタイリング: Tailwind CSS
  - 音声視覚化: `wavesurfer.js`
  - アイコン: `lucide-react`

## フォルダ構造
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

## フェーズ 1: バックエンドのセットアップとコアロジック (Python)
- [x] Python 環境の初期化と `requirements.txt` の作成。
- [x] `audio_processor.py` の実装:
    - ボーカル分離のための `demucs` ロジックを移植。
    - タイムスタンプ付き文字起こしのための `faster-whisper` ロジックを移植。
- [x] `main.py` に FastAPI エンドポイントを作成:
    - `POST /upload`: ファイルアップロードの処理、分離と文字起こしのトリガー。
    - `GET /audio/{filename}`: 音声ファイルの提供。
    - `POST /save`: 修正された文字起こしの保存。

## フェーズ 2: フロントエンドのセットアップ (React + Vite)
- [x] TypeScript と Vite を使用した React プロジェクトを初期化。
- [x] Tailwind CSS のセットアップ。
- [x] ドラッグ・アンド・ドロップ対応の `FileUpload` コンポーネントを作成。
- [x] 波形視覚化のために `wavesurfer.js` を使用した `AudioPlayer` を実装。
- [x] `TranscriptionEditor` を作成:
    - タイムスタンプ付きのテキストセグメントを表示。
    - 再生中に現在のセグメントをハイライト。
    - テキスト編集とクリックによるシークを可能にする。

## フェーズ 3: 統合とブラッシュアップ
- [x] フロントエンドをバックエンド API に接続。
- [ ] キーボードショートカットの実装 (例: Space で再生/一時停止、Ctrl+Enter で保存)。
- [ ] デザインのブラッシュアップ (ダークモード、スムーズなトランジション)。
- [ ] エクスポート機能 (SRT, JSON, TXT)。

## フェーズ 4: テストと最適化
- [ ] 大容量ファイルの処理を検証。
- [ ] 日本語に合わせて Whisper の設定を最適化。
- [ ] レスポンシブな UI の確保。
