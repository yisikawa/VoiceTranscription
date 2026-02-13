import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileAudio, FileVideo, Loader2 } from 'lucide-react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

interface FileUploadProps {
    onFileSelect: (file: File) => void;
    isUploading: boolean;
}

export function cn(...inputs: (string | undefined | null | false)[]) {
    return twMerge(clsx(inputs));
}

export const FileUpload: React.FC<FileUploadProps> = ({ onFileSelect, isUploading }) => {
    const onDrop = useCallback((acceptedFiles: File[]) => {
        if (acceptedFiles.length > 0) {
            onFileSelect(acceptedFiles[0]);
        }
    }, [onFileSelect]);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            'audio/*': [],
            'video/*': []
        },
        disabled: isUploading,
        multiple: false
    });

    return (
        <div
            {...getRootProps()}
            className={cn(
                "border-2 border-dashed rounded-lg p-12 text-center transition-colors cursor-pointer",
                isDragActive ? "border-primary bg-primary/5" : "border-muted-foreground/25 hover:border-primary/50",
                isUploading ? "opacity-50 cursor-not-allowed" : ""
            )}
        >
            <input {...getInputProps()} />
            <div className="flex flex-col items-center justify-center gap-4">
                {isUploading ? (
                    <Loader2 className="h-10 w-10 animate-spin text-primary" />
                ) : (
                    <div className="p-4 bg-primary/10 rounded-full">
                        <Upload className="h-8 w-8 text-primary" />
                    </div>
                )}
                <div className="space-y-1">
                    <p className="text-lg font-medium">
                        {isUploading ? "処理中..." : "ここに音声または動画ファイルをドロップ"}
                    </p>
                    <p className="text-sm text-muted-foreground">
                        対応形式: MP3, WAV, MP4, MOV (200MBまで)
                    </p>
                </div>
            </div>
        </div>
    );
};
