import { describe, it, expect } from 'vitest';
import { generateSRT, generateTXT, formatSrtTime, formatClockTime } from './transcript';
import type { Segment } from '../types';

const segments: Segment[] = [
    { id: 1, start: 0, end: 1.5, text: 'こんにちは' },
    { id: 2, start: 61.25, end: 3723.5, text: '世界' },
];

describe('formatSrtTime', () => {
    it('formats zero', () => {
        expect(formatSrtTime(0)).toBe('00:00:00,000');
    });
    it('formats fractional seconds with millisecond precision', () => {
        expect(formatSrtTime(61.25)).toBe('00:01:01,250');
    });
    it('rolls over hours', () => {
        expect(formatSrtTime(3723.5)).toBe('01:02:03,500');
    });
});

describe('generateSRT', () => {
    it('produces numbered SRT blocks from the given (edited) segments', () => {
        const srt = generateSRT(segments);
        expect(srt).toBe(
            '1\n00:00:00,000 --> 00:00:01,500\nこんにちは\n\n' +
            '2\n00:01:01,250 --> 01:02:03,500\n世界\n\n'
        );
    });
});

describe('generateTXT', () => {
    it('joins segment texts with newlines', () => {
        expect(generateTXT(segments)).toBe('こんにちは\n世界');
    });
});

describe('formatClockTime', () => {
    it('formats with one decimal place', () => {
        expect(formatClockTime(61.25)).toBe('00:01:01.2');
    });
});
