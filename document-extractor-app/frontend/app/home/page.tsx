'use client';

import { useState, useCallback, useRef, useEffect, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/services/api';
import UploadProgress from '@/components/UploadProgress';
import { FileWithMetadata, UploadStatus } from '@/types';
import { formatFileSize } from '@/utils/formatters';

export default function Home() {
  const [files, setFiles] = useState<FileWithMetadata[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<UploadStatus>('idle');
  const [progress, setProgress] = useState(0);
  const [currentFile, setCurrentFile] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const router = useRouter();

  const allowedTypes = useMemo(() => ['application/pdf', 'image/png', 'image/jpeg', 'image/jpg', 'text/plain'], []);
  const maxFileSize = useMemo(() => 10 * 1024 * 1024, []); // 10MB

  const validateFile = (file: File): string | null => {
    if (!allowedTypes.includes(file.type) && !file.name.match(/\.(pdf|png|jpg|jpeg|txt)$/i)) {
      return `File type not allowed: ${file.name}`;
    }
    if (file.size > maxFileSize) {
      return `File too large: ${file.name} (max ${maxFileSize / 1024 / 1024}MB)`;
    }
    return null;
  };

  const handleFiles = useCallback((newFiles: FileList | File[]) => {
    const fileArray = Array.from(newFiles);
    const validFiles: FileWithMetadata[] = [];
    const errors: string[] = [];

    fileArray.forEach((file) => {
      const error = validateFile(file);
      if (error) {
        errors.push(error);
      } else {
        validFiles.push({
          file: file,
          metadata: {
            id: `${Date.now()}-${Math.random()}`,
            status: 'pending',
          },
        });
      }
    });

    if (errors.length > 0) {
      alert(errors.join('\n'));
    }

    if (validFiles.length > 0) {
      setFiles((prev) => [...prev, ...validFiles]);
    }
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files) {
      handleFiles(e.dataTransfer.files);
    }
  }, [handleFiles]);

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      handleFiles(e.target.files);
    }
  }, [handleFiles]);

  const removeFile = useCallback((fileId: string) => {
    setFiles((prev) => prev.filter((f) => f.metadata.id !== fileId));
  }, []);

  const simulateProgress = useCallback((start: number, end: number, duration: number) => {
    const startTime = Date.now();
    let animationFrameId: number;
    
    const updateProgress = () => {
      const elapsed = Date.now() - startTime;
      const progressValue = Math.min(start + (end - start) * (elapsed / duration), end);
      setProgress(progressValue);

      if (progressValue < end) {
        animationFrameId = requestAnimationFrame(updateProgress);
      }
    };
    
    animationFrameId = requestAnimationFrame(updateProgress);
    
    // Return cleanup function
    return () => {
      if (animationFrameId) {
        cancelAnimationFrame(animationFrameId);
      }
    };
  }, []);

  const handleUpload = useCallback(async () => {
    if (files.length === 0) return;

    let progressCleanup: (() => void) | undefined;
    let processingTimeout: NodeJS.Timeout | undefined;
    let redirectTimeout: NodeJS.Timeout | undefined;

    try {
      setUploadStatus('uploading');
      setError(null);
      setProgress(0);
      
      // Mark all files as uploading
      setFiles((prev) => 
        prev.map((f) => ({ ...f, metadata: { ...f.metadata, status: 'uploading' } }))
      );

      // Simulate upload progress (0-30%)
      progressCleanup = simulateProgress(0, 30, 500);
      setCurrentFile(`Uploading ${files.length} file(s)...`);

      // Extract actual File objects for upload
      const fileObjects = files.map((f) => f.file);
      
      // Switch to processing status (30-90%)
      processingTimeout = setTimeout(() => {
        setUploadStatus('processing');
        setCurrentFile('Extracting data with AI...');
        progressCleanup?.();
        progressCleanup = simulateProgress(30, 90, 2000);
      }, 500);

      // Make the actual API call
      await api.uploadDocuments(fileObjects);
      
      // Clean up timeouts
      if (processingTimeout) clearTimeout(processingTimeout);
      progressCleanup?.();
      
      // Complete progress (90-100%)
      setUploadStatus('completed');
      setProgress(100);
      setCurrentFile('Processing complete!');
      
      // Wait a moment to show completion, then redirect
      redirectTimeout = setTimeout(() => {
        router.push('/documents');
      }, 1500);
    } catch (err: any) {
      progressCleanup?.();
      if (processingTimeout) clearTimeout(processingTimeout);
      const errorMessage = err.response?.data?.error || err.message || 'Upload failed';
      setError(errorMessage);
      setUploadStatus('error');
      setProgress(0);
      setFiles((prev) => prev.map((f => ({ 
        ...f, 
        metadata: { ...f.metadata, status: 'error', error: errorMessage } 
      }))));
      
      // Redirect after showing error for 2 seconds
      redirectTimeout = setTimeout(() => {
        router.push('/documents');
      }, 2000);
    }
  }, [files, router, simulateProgress]);

  // Reset progress when upload status changes to idle
  useEffect(() => {
    if (uploadStatus === 'idle') {
      setProgress(0);
      setCurrentFile('');
    }
  }, [uploadStatus]);

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4 max-w-4xl">
        <div className="mb-6">
          <h1 className="text-3xl font-bold mb-2">Upload Documents</h1>
          <p className="text-gray-600">Upload documents to extract structured data</p>
        </div>

        {/* Progress Bar - Show when uploading/processing */}
        {(uploadStatus === 'uploading' || uploadStatus === 'processing' || uploadStatus === 'completed' || uploadStatus === 'error') && (
          <UploadProgress
            progress={progress}
            status={uploadStatus === 'completed' ? 'completed' : uploadStatus === 'error' ? 'error' : uploadStatus === 'processing' ? 'processing' : 'uploading'}
            currentFile={currentFile}
            errorMessage={error || undefined}
          />
        )}

        {/* Drag and Drop Area */}
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={`border-2 border-dashed rounded-lg p-8 text-center transition-all duration-300 ${
            isDragging
              ? 'border-blue-500 bg-blue-50 scale-105 shadow-lg'
              : 'border-gray-300 bg-gray-50 hover:border-blue-400 hover:bg-blue-50/50 hover:shadow-md'
          } ${uploadStatus !== 'idle' ? 'opacity-50 pointer-events-none' : ''}`}
        >
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept=".pdf,.png,.jpg,.jpeg,.txt"
            onChange={handleFileInput}
            className="hidden"
            disabled={uploadStatus !== 'idle'}
          />
          <div className="space-y-4">
            <div>
              <p className="text-lg font-medium text-gray-700">
                Drag and drop files here, or click to select
              </p>
              <p className="text-sm text-gray-500 mt-2">
                Supported formats: PDF, PNG, JPG, JPEG, TXT (max 10MB per file)
              </p>
            </div>
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={uploadStatus !== 'idle'}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              Select Files
            </button>
          </div>
        </div>

        {/* File List */}
        {files.length > 0 && (
          <div className="mt-6 bg-white border rounded-lg p-4">
            <h2 className="text-xl font-semibold mb-4">Selected Files</h2>
            <div className="space-y-2">
              {files.map((fileWithMeta) => (
                <div
                  key={fileWithMeta.metadata.id}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                >
                  <div className="flex-1">
                    <p className="font-medium">{fileWithMeta.file.name}</p>
                    <p className="text-sm text-gray-500">
                      {formatFileSize(fileWithMeta.file.size)}
                    </p>
                  </div>
                  {uploadStatus === 'idle' && (
                    <button
                      onClick={() => removeFile(fileWithMeta.metadata.id)}
                      className="ml-4 text-red-600 hover:text-red-800"
                    >
                      Remove
                    </button>
                  )}
                </div>
              ))}
            </div>
            <div className="mt-4 flex gap-4">
              <button
                onClick={handleUpload}
                disabled={uploadStatus !== 'idle'}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
              >
                {uploadStatus === 'uploading' || uploadStatus === 'processing' ? 'Processing...' : 'Upload Files'}
              </button>
              {uploadStatus === 'idle' && (
                <button
                  onClick={() => setFiles([])}
                  className="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
                >
                  Clear All
                </button>
              )}
            </div>
          </div>
        )}

        {/* Error Display */}
        {error && uploadStatus === 'error' && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-800">{error}</p>
          </div>
        )}
      </div>
    </div>
  );
}

