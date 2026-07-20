import React, { useCallback, useState } from 'react';
import { UploadCloud, File as FileIcon, X } from 'lucide-react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

interface UploadDropzoneProps {
  onFileSelect: (file: File) => void;
  maxSizeMB?: number;
  acceptedTypes?: string[];
  disabled?: boolean;
}

export const UploadDropzone: React.FC<UploadDropzoneProps> = ({ 
  onFileSelect, 
  maxSizeMB = 100,
  acceptedTypes = ['text/csv', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/json'],
  disabled = false
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (disabled) return;
    
    if (e.type === "dragenter" || e.type === "dragover") {
      setIsDragging(true);
    } else if (e.type === "dragleave") {
      setIsDragging(false);
    }
  }, [disabled]);

  const validateFile = (file: File): boolean => {
    setError(null);
    if (!acceptedTypes.includes(file.type) && !file.name.endsWith('.csv')) {
      setError("File type not supported. Please upload CSV, Excel, or JSON.");
      return false;
    }
    if (file.size > maxSizeMB * 1024 * 1024) {
      setError(`File exceeds ${maxSizeMB}MB limit.`);
      return false;
    }
    return true;
  };

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    if (disabled) return;

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (validateFile(file)) {
        setSelectedFile(file);
        onFileSelect(file);
      }
    }
  }, [disabled, onFileSelect]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (disabled) return;
    
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (validateFile(file)) {
        setSelectedFile(file);
        onFileSelect(file);
      }
    }
  };

  const removeFile = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (disabled) return;
    setSelectedFile(null);
    setError(null);
  };

  return (
    <div className="w-full max-w-2xl mx-auto mt-8">
      <div 
        className={cn(
          "relative flex flex-col items-center justify-center p-12 border-2 border-dashed rounded-xl transition-all duration-200 ease-in-out bg-card",
          isDragging ? "border-primary bg-primary/5" : "border-muted-foreground/25 hover:border-primary/50 hover:bg-muted/50",
          disabled && "opacity-50 cursor-not-allowed",
          selectedFile && "border-primary bg-primary/5"
        )}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => !disabled && !selectedFile && document.getElementById('file-upload')?.click()}
      >
        <input 
          id="file-upload"
          type="file" 
          className="hidden" 
          onChange={handleChange}
          disabled={disabled}
          accept=".csv,.xlsx,.json,text/csv,application/json"
        />

        {!selectedFile ? (
          <>
            <div className="p-4 bg-primary/10 rounded-full mb-4">
              <UploadCloud className="w-8 h-8 text-primary" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Upload your dataset</h3>
            <p className="text-sm text-muted-foreground text-center mb-6">
              Drag and drop your file here, or click to browse
            </p>
            <div className="flex gap-2 text-xs font-medium text-muted-foreground">
              <span className="px-2 py-1 rounded-md bg-muted">CSV</span>
              <span className="px-2 py-1 rounded-md bg-muted">Excel</span>
              <span className="px-2 py-1 rounded-md bg-muted">JSON</span>
            </div>
            {error && <p className="mt-4 text-sm font-medium text-destructive">{error}</p>}
          </>
        ) : (
          <div className="flex items-center gap-4 p-4 rounded-lg bg-background border shadow-sm w-full">
            <div className="p-3 bg-primary/10 rounded-md">
              <FileIcon className="w-6 h-6 text-primary" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">{selectedFile.name}</p>
              <p className="text-xs text-muted-foreground">{(selectedFile.size / (1024 * 1024)).toFixed(2)} MB</p>
            </div>
            <button 
              onClick={removeFile}
              disabled={disabled}
              className="p-2 text-muted-foreground hover:text-destructive hover:bg-destructive/10 rounded-full transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
