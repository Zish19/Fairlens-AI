import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

export interface AnalysisConfig {
    schema_version: number;
    training: {
        algorithm: string;
        random_state: number;
        test_size: number;
    };
    fairness: {
        target_column: string;
        sensitive_attribute: string;
        positive_label: any;
        metrics: string[];
    };
}

export interface Recommendation {
    severity: string;
    title: string;
    description: string;
    recommendedAction: string;
}

export interface MetricResultResponse {
    metric_name: string;
    metric_value: number;
    subgroup?: string;
    threshold?: number;
    interpretation?: string;
}

export interface AnalysisResponse {
    id: string;
    dataset_version_id: string;
    status: string;
    config: AnalysisConfig;
    metrics: MetricResultResponse[];
    recommendations: Recommendation[];
    created_at: string;
    updated_at: string;
}

export interface DatasetVersionAnalyses {
    version_id: string;
    storage_path: string;
    created_at: string;
    analyses: AnalysisResponse[];
}

export interface DatasetAnalysesResponse {
    dataset_id: string;
    versions: DatasetVersionAnalyses[];
}

export const analysisApi = {
    async submitAnalysis(datasetVersionId: string, config: AnalysisConfig): Promise<AnalysisResponse> {
        const response = await axios.post(`${API_BASE_URL}/datasets/${datasetVersionId}/analyze`, { config });
        return response.data;
    },

    async getAnalysis(analysisId: string): Promise<AnalysisResponse> {
        const response = await axios.get(`${API_BASE_URL}/analyses/${analysisId}`);
        return response.data;
    },

    async listAnalyses(skip = 0, limit = 50, status?: string): Promise<AnalysisResponse[]> {
        let url = `${API_BASE_URL}/analyses?skip=${skip}&limit=${limit}`;
        if (status) url += `&status=${status}`;
        const response = await axios.get(url);
        return response.data;
    },

    async listDatasetAnalyses(datasetId: string): Promise<DatasetAnalysesResponse> {
        const response = await axios.get(`${API_BASE_URL}/datasets/${datasetId}/analyses`);
        return response.data;
    },

    async getExplainability(analysisId: string): Promise<any> {
        const response = await axios.get(`${API_BASE_URL}/analyses/${analysisId}/explainability`);
        return response.data;
    },

    async getInsights(analysisId: string): Promise<any> {
        const response = await axios.get(`${API_BASE_URL}/analyses/${analysisId}/insights`);
        return response.data;
    }
};
