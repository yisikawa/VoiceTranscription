import React, { useEffect, useRef, useState } from 'react';
import WaveSurfer from 'wavesurfer.js';
import { Play, Pause, Download, FileText, Music } from 'lucide-react';
import type { Segment, TranscriptionResult } from '../types';

interface TranscriptionEditorProps {
    audioUrl: string;
    transcription: TranscriptionResult;
    fileName: string;
    onSave: (segments: Segment[]) => void;
    onExport: (format: 'srt' | 'txt' | 'json') => void;
}

export const TranscriptionEditor: React.FC<TranscriptionEditorProps> = ({
    audioUrl,
    transcription,
    fileName,
    onSave,
    onExport
}) => {
    // ... (rest of the component logic remains unchanged until render)
    const containerRef = useRef<HTMLDivElement>(null);
    const wavesurfer = useRef<WaveSurfer | null>(null);
    const [isPlaying, setIsPlaying] = useState(false);
    const [currentTime, setCurrentTime] = useState(0);
    const [segments, setSegments] = useState<Segment[]>(transcription.segments);
    const [activeSegmentId, setActiveSegmentId] = useState<number | string | null>(null);

    // Initialize WaveSurfer
    useEffect(() => {
        if (!containerRef.current) return;

        wavesurfer.current = WaveSurfer.create({
            container: containerRef.current,
            waveColor: '#4f46e5',
            progressColor: '#818cf8',
            cursorColor: '#333',
            barWidth: 2,
            barGap: 3,
            height: 80,
            normalize: true,
            url: audioUrl,
        });

        wavesurfer.current.on('ready', () => {
            console.log('WaveSurfer 準備完了');
        });

        wavesurfer.current.on('timeupdate', (time) => {
            setCurrentTime(time);
        });

        wavesurfer.current.on('interaction', () => {
            if (wavesurfer.current) {
                setCurrentTime(wavesurfer.current.getCurrentTime());
            }
        });

        wavesurfer.current.on('finish', () => setIsPlaying(false));
        wavesurfer.current.on('play', () => setIsPlaying(true));
        wavesurfer.current.on('pause', () => setIsPlaying(false));

        return () => {
            wavesurfer.current?.destroy();
        };
    }, [audioUrl]);

    // Sync active segment based on time
    useEffect(() => {
        const active = segments.find(
            seg => currentTime >= seg.start && currentTime <= seg.end
        );
        setActiveSegmentId(active ? active.id : null);

        // Auto-scroll to active segment
        if (active) {
            const element = document.getElementById(`segment-${active.id}`);
            if (element) {
                element.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }
        }
    }, [currentTime, segments]);

    const togglePlay = () => {
        if (wavesurfer.current) {
            wavesurfer.current.playPause();
            setIsPlaying(!isPlaying);
        }
    };

    const handleDownloadAudio = async () => {
        try {
            const response = await fetch(audioUrl);
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            const baseName = fileName ? fileName.replace(/\.[^/.]+$/, "") : "audio";
            a.download = `${baseName}_vocals.wav`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
        } catch (error) {
            console.error('Audio download failed', error);
            alert('音声のダウンロードに失敗しました');
        }
    };

    const handleSegmentClick = (start: number) => {
        if (wavesurfer.current) {
            wavesurfer.current.setTime(start);
            // wavesurfer.current.play(); // Optional: Auto-play on click
            // setIsPlaying(true);
        }
    };

    const handleTextChange = (id: number | string, newText: string) => {
        setSegments(prev =>
            prev.map(seg => (seg.id === id ? { ...seg, text: newText } : seg))
        );
    };

    // Keyboard shortcut for Play/Pause
    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if (e.code === 'Space' && document.activeElement?.tagName !== 'TEXTAREA') {
                e.preventDefault(); // Prevent scrolling
                togglePlay();
            }
            // Add more shortcuts like Ctrl+Enter to save?
        };
        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [isPlaying]); // Re-bind with updated isPlaying state

    return (
        <div className="flex flex-col h-full bg-background rounded-lg shadow-lg border">
            {/* Top Bar: Waveform & Controls */}
            <div className="p-4 border-b bg-card z-10 sticky top-0">
                <div ref={containerRef} className="w-full mb-4" />

                <div className="flex items-center justify-between">
                    <button
                        onClick={togglePlay}
                        className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
                    >
                        {isPlaying ? <Pause size={20} /> : <Play size={20} />}
                        {isPlaying ? "一時停止" : "再生"}
                    </button>

                    <div className="flex gap-2">
                        <button
                            onClick={handleDownloadAudio}
                            className="flex items-center gap-2 px-4 py-2 bg-secondary text-secondary-foreground rounded-md hover:bg-secondary/80 transition-colors"
                        >
                            <Music size={18} /> Voice保存
                        </button>
                        <button
                            onClick={() => onSave(segments)}
                            className="flex items-center gap-2 px-4 py-2 bg-secondary text-secondary-foreground rounded-md hover:bg-secondary/80 transition-colors"
                        >
                            <FileText size={18} /> テキスト保存
                        </button>
                        <button
                            onClick={() => onExport('srt')}
                            className="flex items-center gap-2 px-4 py-2 bg-secondary text-secondary-foreground rounded-md hover:bg-secondary/80 transition-colors"
                        >
                            <Download size={18} /> SRT出力
                        </button>
                    </div>
                </div>
                <div className="text-center text-sm text-muted-foreground mt-2">
                    {formatTime(currentTime)}
                </div>
            </div>

            {/* Main Content: Transcription List */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {segments.map((segment) => (
                    <div
                        key={segment.id}
                        id={`segment-${segment.id}`}
                        className={`p-4 rounded-lg border transition-all duration-200 ${activeSegmentId === segment.id
                            ? 'bg-accent border-primary shadow-sm scale-[1.01]'
                            : 'hover:bg-muted/50 border-transparent'
                            }`}
                    >
                        <div
                            className="flex items-center gap-2 mb-2 cursor-pointer text-xs font-mono text-muted-foreground hover:text-primary"
                            onClick={() => handleSegmentClick(segment.start)}
                        >
                            <span className="bg-muted px-1.5 py-0.5 rounded">{formatTime(segment.start)}</span>
                            <span>→</span>
                            <span className="bg-muted px-1.5 py-0.5 rounded">{formatTime(segment.end)}</span>
                        </div>

                        <textarea
                            className="w-full bg-transparent resize-none outline-none text-lg leading-relaxed font-medium p-1 rounded focus:bg-background focus:ring-1 focus:ring-ring"
                            value={segment.text}
                            onChange={(e) => handleTextChange(segment.id, e.target.value)}
                            rows={Math.max(1, Math.ceil(segment.text.length / 60))} // Auto-grow somewhat
                        />
                    </div>
                ))}
            </div>
        </div>
    );
};

// Helper for HH:MM:SS
function formatTime(seconds: number): string {
    const date = new Date(0);
    date.setSeconds(seconds);
    return date.toISOString().substr(11, 8) + "." + Math.floor((seconds % 1) * 10).toString();
}
