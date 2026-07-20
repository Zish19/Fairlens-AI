import React from 'react';
import { cn } from './UploadDropzone';

interface ProgressBarProps {
  progress: number;
  label?: string;
  sublabel?: string;
  status?: 'active' | 'success' | 'error';
}

export const ProgressBar: React.FC<ProgressBarProps> = ({ 
  progress, 
  label = "Processing...", 
  sublabel,
  status = 'active'
}) => {
  const safeProgress = Math.min(100, Math.max(0, progress));
  
  return (
    <div className="w-full max-w-2xl mx-auto mt-6">
      <div className="flex justify-between items-end mb-2">
        <div>
          <span className="text-sm font-medium text-foreground">{label}</span>
          {sublabel && (
            <span className="ml-2 text-xs text-muted-foreground">{sublabel}</span>
          )}
        </div>
        <span className="text-sm font-semibold">{Math.round(safeProgress)}%</span>
      </div>
      
      <div className="w-full h-3 overflow-hidden rounded-full bg-secondary">
        <div 
          className={cn(
            "h-full transition-all duration-500 ease-out rounded-full",
            status === 'active' && "bg-primary relative overflow-hidden",
            status === 'success' && "bg-green-500",
            status === 'error' && "bg-destructive",
          )}
          style={{ width: `${safeProgress}%` }}
        >
          {status === 'active' && (
            <div className="absolute top-0 left-0 right-0 bottom-0 bg-[linear-gradient(45deg,rgba(255,255,255,.15)25%,transparent_25%,transparent_50%,rgba(255,255,255,.15)_50%,rgba(255,255,255,.15)_75%,transparent_75%,transparent)] bg-[length:1rem_1rem] animate-[progress_1s_linear_infinite]" />
          )}
        </div>
      </div>
    </div>
  );
};
