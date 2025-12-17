'use client';

interface UploadProgressProps {
  progress: number;
  status: 'uploading' | 'processing' | 'completed' | 'error';
  currentFile?: string;
  errorMessage?: string;
}

export default function UploadProgress({
  progress,
  status,
  currentFile,
  errorMessage,
}: UploadProgressProps) {
  const getStatusText = () => {
    switch (status) {
      case 'uploading':
        return 'Uploading files...';
      case 'processing':
        return 'Extracting data from documents...';
      case 'completed':
        return 'Upload completed successfully!';
      case 'error':
        return 'Upload failed';
      default:
        return 'Processing...';
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case 'uploading':
        return 'bg-blue-600';
      case 'processing':
        return 'bg-blue-600';
      case 'completed':
        return 'bg-green-600';
      case 'error':
        return 'bg-red-600';
      default:
        return 'bg-blue-600';
    }
  };

  return (
    <div className="mt-6 bg-white border rounded-lg p-6 shadow-sm">
      <div className="mb-4">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-lg font-semibold text-gray-800">{getStatusText()}</h3>
          <span className="text-sm font-medium text-gray-600">{Math.round(progress)}%</span>
        </div>
        {currentFile && (
          <p className="text-sm text-gray-600 mb-2">Processing: {currentFile}</p>
        )}
      </div>

      {/* Progress Bar */}
      <div className="w-full bg-gray-200 rounded-full h-3 mb-4 overflow-hidden">
        <div
          className={`h-full transition-all duration-300 ease-out ${getStatusColor()}`}
          style={{ width: `${progress}%` }}
        />
      </div>

      {/* Status Details */}
      <div className="text-sm text-gray-600">
        {status === 'uploading' && (
          <p>Uploading files to server...</p>
        )}
        {status === 'processing' && (
          <p>Using AI to extract structured data from your documents. This may take a minute...</p>
        )}
        {status === 'completed' && (
          <p className="text-green-700 font-medium">✓ All files processed successfully</p>
        )}
        {status === 'error' && errorMessage && (
          <p className="text-red-700 font-medium">✗ {errorMessage}</p>
        )}
      </div>
    </div>
  );
}

