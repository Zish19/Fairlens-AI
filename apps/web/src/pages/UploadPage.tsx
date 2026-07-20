import React, { useState, useEffect } from 'react';
import { UploadDropzone } from '../components/UploadDropzone';
import { ProgressBar } from '../components/ProgressBar';
import { ProfileSummaryCards } from '../components/ProfileSummaryCards';
import { uploadDataset, getJobStatus, type UploadResponse } from '../api/datasets';

export const UploadPage: React.FC = () => {
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'processing' | 'completed' | 'error'>('idle');
  const [uploadProgress, setUploadProgress] = useState(0);
  const [jobProgress, setJobProgress] = useState(0);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  
  const [jobId, setJobId] = useState<string | null>(null);
  const [profileSummary, setProfileSummary] = useState<any>(null);

  const handleFileSelect = async (file: File) => {
    setUploadStatus('uploading');
    setUploadProgress(0);
    setErrorMessage(null);
    setProfileSummary(null);

    try {
      const response: UploadResponse = await uploadDataset(file, (progressEvent) => {
        if (progressEvent.total) {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(percentCompleted);
        }
      });
      
      setUploadStatus('processing');
      setJobId(response.data.jobId);
    } catch (error: any) {
      setUploadStatus('error');
      setErrorMessage(error.response?.data?.detail || error.message || "Failed to upload file");
    }
  };

  useEffect(() => {
    let intervalId: ReturnType<typeof setInterval>;

    if (uploadStatus === 'processing' && jobId) {
      // Simulate progress bar filling up while we wait for the job
      setJobProgress(0);
      const fakeProgressInterval = setInterval(() => {
        setJobProgress(p => (p < 95 ? p + 5 : p));
      }, 500);

      // Poll for job status
      const checkJob = async () => {
        try {
          const statusRes = await getJobStatus(jobId);
          if (statusRes.status === 'COMPLETED') {
            clearInterval(intervalId);
            clearInterval(fakeProgressInterval);
            setJobProgress(100);
            setProfileSummary(statusRes.result);
            // Wait a beat before showing completed UI
            setTimeout(() => setUploadStatus('completed'), 500);
          } else if (statusRes.status === 'FAILED') {
            clearInterval(intervalId);
            clearInterval(fakeProgressInterval);
            setUploadStatus('error');
            setErrorMessage("Dataset profiling failed on the server.");
          }
        } catch (error) {
          console.error("Failed to poll job status", error);
        }
      };

      intervalId = setInterval(checkJob, 2000);
      checkJob(); // Check immediately

      return () => {
        clearInterval(intervalId);
        clearInterval(fakeProgressInterval);
      };
    }
  }, [uploadStatus, jobId]);

  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto px-4 py-12">
        <div className="max-w-3xl mx-auto text-center mb-12">
          <h1 className="text-4xl font-bold tracking-tight mb-4">Upload Dataset</h1>
          <p className="text-lg text-muted-foreground">
            Securely upload your CSV, JSON, or Excel dataset for automated profiling and bias analysis.
          </p>
        </div>

        {uploadStatus === 'idle' && (
          <UploadDropzone onFileSelect={handleFileSelect} />
        )}

        {uploadStatus === 'uploading' && (
          <div className="py-12">
            <ProgressBar 
              progress={uploadProgress} 
              label="Uploading dataset to server..." 
            />
          </div>
        )}

        {uploadStatus === 'processing' && (
          <div className="py-12">
            <ProgressBar 
              progress={jobProgress} 
              label="Profiling Dataset..." 
              sublabel="Analyzing distributions and calculating statistics"
            />
          </div>
        )}

        {uploadStatus === 'completed' && profileSummary && (
          <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <div className="bg-green-500/10 text-green-600 border border-green-500/20 p-4 rounded-lg flex items-center justify-center font-medium">
              Dataset profiled successfully!
            </div>
            <ProfileSummaryCards summary={profileSummary} />
            
            <div className="text-center mt-8">
              <button 
                onClick={() => setUploadStatus('idle')}
                className="px-6 py-2 bg-primary text-primary-foreground font-medium rounded-lg hover:bg-primary/90 transition-colors"
              >
                Upload Another Dataset
              </button>
            </div>
          </div>
        )}

        {uploadStatus === 'error' && (
          <div className="max-w-2xl mx-auto mt-8 p-6 bg-destructive/10 border border-destructive/20 rounded-xl text-center">
            <h3 className="text-lg font-semibold text-destructive mb-2">Upload Failed</h3>
            <p className="text-muted-foreground mb-6">{errorMessage}</p>
            <button 
              onClick={() => setUploadStatus('idle')}
              className="px-6 py-2 bg-secondary text-secondary-foreground font-medium rounded-lg hover:bg-secondary/80 transition-colors"
            >
              Try Again
            </button>
          </div>
        )}
      </main>
    </div>
  );
};
