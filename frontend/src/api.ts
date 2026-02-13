import axios from 'axios';
import type { TaskStatus } from './types';

const API_BASE_URL = 'http://localhost:8001';

export const uploadFile = async (file: File): Promise<string> => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await axios.post<{ task_id: string }>(`${API_BASE_URL}/upload`, formData);
    return response.data.task_id;
};

export const getTaskStatus = async (taskId: string): Promise<TaskStatus> => {
    const response = await axios.get<TaskStatus>(`${API_BASE_URL}/tasks/${taskId}`);
    return response.data;
};

export const getAudioUrl = (taskId: string, filename: string): string => {
    return `${API_BASE_URL}/audio/${taskId}/${filename}`;
};

export const saveTranscription = async (taskId: string, segments: any[]): Promise<void> => {
    await axios.post(`${API_BASE_URL}/save/${taskId}`, segments);
};
