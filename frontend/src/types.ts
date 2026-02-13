export interface Segment {
    id: number | string;
    start: number;
    end: number;
    text: string;
}

export interface TranscriptionResult {
    language: string;
    segments: Segment[];
}

export interface TaskStatus {
    task_id: string;
    start_time?: number;
    status: 'processing' | 'completed' | 'failed';
    result?: {
        original_filename: string;
        extracted_audio: string;
        vocals_audio: string;
        transcription: TranscriptionResult;
    };
    error?: string;
}
