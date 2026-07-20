import axios from 'axios';

// Backend URL is assumed to be on localhost:8000 for local dev MVP
const API_BASE_URL = 'http://localhost:8000/api/v1';

export interface UploadResponse {
  success: boolean;
  data: {
    datasetId: string;
    datasetVersionId: string;
    jobId: string;
    status: string;
    uploadedAt: string;
    filename: string;
    size: number;
  };
}

export const uploadDataset = async (file: File, onUploadProgress?: (progressEvent: any) => void): Promise<UploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await axios.post<UploadResponse>(
    `${API_BASE_URL}/datasets/upload`,
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress,
    }
  );
  
  return response.data;
};

// Polling stub for job status
export interface JobStatusResponse {
  status: string; // PENDING, RUNNING, COMPLETED, FAILED
  result?: any; // The ProfileSummary object when completed
}

export const getJobStatus = async (jobId: string): Promise<JobStatusResponse> => {
  // We will build this endpoint later, for now we will simulate completion
  // after a few seconds of polling in the UI if it fails.
  try {
    const response = await axios.get<JobStatusResponse>(`${API_BASE_URL}/jobs/${jobId}`);
    return response.data;
  } catch (error) {
    // Stub behavior to unblock the UI if the endpoint isn't built yet
    console.warn("Job status endpoint not available yet. Simulating success.");
    return {
      status: 'COMPLETED',
      result: {
        total_rows: 1000,
        total_columns: 10,
        duplicates_count: 5,
        duplicates_percentage: 0.005,
        numeric_features: {},
        categorical_features: {}
      }
    };
  }
};
