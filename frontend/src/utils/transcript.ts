import type { Segment } from '../types';

const pad = (n: number, width = 2) => String(n).padStart(width, '0');

/** SRT形式のタイムスタンプ HH:MM:SS,mmm */
export function formatSrtTime(seconds: number): string {
    const totalMs = Math.round(seconds * 1000);
    const h = Math.floor(totalMs / 3600000);
    const m = Math.floor((totalMs % 3600000) / 60000);
    const s = Math.floor((totalMs % 60000) / 1000);
    const ms = totalMs % 1000;
    return `${pad(h)}:${pad(m)}:${pad(s)},${pad(ms, 3)}`;
}

/** エディタ表示用 HH:MM:SS.d（小数1桁） */
export function formatClockTime(seconds: number): string {
    const total = Math.floor(seconds);
    const h = Math.floor(total / 3600);
    const m = Math.floor((total % 3600) / 60);
    const s = total % 60;
    const tenth = Math.floor((seconds % 1) * 10);
    return `${pad(h)}:${pad(m)}:${pad(s)}.${tenth}`;
}

export function generateSRT(segments: Segment[]): string {
    return segments
        .map((seg, i) =>
            `${i + 1}\n${formatSrtTime(seg.start)} --> ${formatSrtTime(seg.end)}\n${seg.text}\n\n`)
        .join('');
}

export function generateTXT(segments: Segment[]): string {
    return segments.map(seg => seg.text).join('\n');
}
