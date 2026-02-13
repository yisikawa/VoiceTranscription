import { useState, useEffect } from 'react';
import { FileAudio, Clock, CheckCircle2, AlertCircle } from 'lucide-react';

import { FileUpload } from './components/FileUpload';
import { TranscriptionEditor } from './components/TranscriptionEditor';
import { uploadFile, getTaskStatus, getAudioUrl } from './api';
import type { TaskStatus } from './types';

// Simple SRT generator for browser download
const generateSRT = (segments: any[]) => {
  const formatTime = (seconds: number) => {
    const date = new Date(0);
    date.setSeconds(seconds);
    const time = date.toISOString().substr(11, 12).replace('.', ',');
    return time;
  };

  return segments.map((seg, i) => {
    return `${i + 1}\n${formatTime(seg.start)} --> ${formatTime(seg.end)}\n${seg.text}\n\n`;
  }).join('');
};

const generateTXT = (segments: any[]) => {
  return segments.map(seg => seg.text).join('\n');
};

function App() {
  const [taskId, setTaskId] = useState<string | null>(null);
  const [status, setStatus] = useState<TaskStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  // Polling for status
  useEffect(() => {
    if (!taskId || (status?.status === 'completed' || status?.status === 'failed')) return;

    const interval = setInterval(async () => {
      try {
        const result = await getTaskStatus(taskId);
        setStatus(result);
        if (result.status === 'failed') {
          setError(result.error || 'Unknown error occurred');
        }
      } catch (err: any) {
        setError(err.message);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [taskId, status]);

  const handleFileSelect = async (file: File) => {
    setIsUploading(true);
    setError(null);
    try {
      const id = await uploadFile(file);
      setTaskId(id);
      setStatus({ task_id: id, status: 'processing' });
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsUploading(false);
    }
  };

  const handleSave = (segments: any[]) => {
    const textContent = generateTXT(segments);
    const blob = new Blob([textContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    // Remove original extension if possible and append .txt
    const originalName = status?.result?.original_filename || 'transcript';
    const baseName = originalName.replace(/\.[^/.]+$/, "");
    a.download = `${baseName}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleExport = () => {
    if (!status?.result?.transcription.segments) return;

    const srtContent = generateSRT(status.result.transcription.segments);
    const blob = new Blob([srtContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${status.result.original_filename || 'transcript'}.srt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col font-sans">
      <header className="p-4 border-b bg-card shadow-sm sticky top-0 z-50">
        <div className="container mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="p-2 bg-primary rounded-lg">
              <FileAudio className="h-6 w-6 text-primary-foreground" />
            </div>
            <h1 className="text-xl font-bold tracking-tight">Voice Transcription Studio</h1>
          </div>
          <div className="text-sm text-muted-foreground">
            Powered by Faster-Whisper & Demucs (日本語対応版)
          </div>
        </div>
      </header>

      <main className="flex-1 container mx-auto p-4 md:p-8">

        {/* State: Initial & Uploading */}
        {!taskId && (
          <div className="max-w-xl mx-auto mt-20">
            <div className="text-center mb-10">
              <h2 className="text-3xl font-bold mb-4">文字起こしを始める</h2>
              <p className="text-muted-foreground text-lg">
                音声または動画ファイルをアップロードしてください。ボーカル分離と文字起こしを自動で行います。
              </p>
            </div>

            <FileUpload onFileSelect={handleFileSelect} isUploading={isUploading} />

            {error && (
              <div className="mt-6 p-4 bg-destructive/10 text-destructive rounded-lg flex items-center gap-3 border border-destructive/20">
                <AlertCircle size={20} />
                <span>{error}</span>
              </div>
            )}
          </div>
        )}

        {/* State: Processing */}
        {taskId && status?.status === 'processing' && (
          <div className="max-w-xl mx-auto mt-20 text-center space-y-8">
            <div className="relative w-24 h-24 mx-auto">
              <div className="absolute inset-0 border-4 border-muted rounded-full"></div>
              <div className="absolute inset-0 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
              <Clock className="absolute inset-0 m-auto text-primary h-8 w-8 animate-pulse" />
            </div>
            <div>
              <h3 className="text-2xl font-semibold">ファイルを処理中...</h3>
              <p className="text-muted-foreground mt-2">
                音声抽出・ボーカル分離・AI文字起こしを実行しています。
                <br />ファイルの長さによっては数分かかる場合があります。
              </p>
              <div className="mt-8 p-4 bg-secondary rounded-lg inline-block text-sm font-mono text-left">
                <p className="text-muted-foreground">タスクID: {taskId}</p>
                <p className="status-blink mt-1 text-primary">ステータス: {status.status}</p>
              </div>
            </div>
          </div>
        )}

        {/* State: Completed (Show Editor) */}
        {taskId && status?.status === 'completed' && status.result && (
          <div className="h-[calc(100vh-140px)] flex flex-col gap-4 animate-in fade-in zoom-in duration-300">
            <div className="flex items-center gap-2 mb-2">
              <CheckCircle2 className="text-green-500 h-5 w-5" />
              <span className="font-medium text-green-600">処理完了</span>
              <span className="text-muted-foreground text-sm ml-auto">
                ファイル: {status.result.original_filename}
              </span>
            </div>

            <TranscriptionEditor
              audioUrl={getAudioUrl(taskId, status.result.vocals_audio)}
              transcription={status.result.transcription}
              fileName={status.result.original_filename}
              onSave={handleSave}
              onExport={handleExport}
            />
          </div>
        )}

        {/* State: Failed */}
        {taskId && status?.status === 'failed' && (
          <div className="max-w-xl mx-auto mt-20 text-center">
            <div className="p-6 bg-destructive/10 text-destructive rounded-lg border border-destructive/20 mb-6">
              <AlertCircle className="h-12 w-12 mx-auto mb-4" />
              <h3 className="text-xl font-bold mb-2">処理失敗</h3>
              <p>{error || status.error}</p>
            </div>
            <button
              onClick={() => { setTaskId(null); setStatus(null); setError(null); }}
              className="px-6 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
            >
              別のファイルを試す
            </button>
          </div>
        )}

      </main>
    </div>
  );
}

export default App;
