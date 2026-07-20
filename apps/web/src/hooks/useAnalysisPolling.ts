import { useState, useEffect, useCallback } from 'react';
import { analysisApi, AnalysisResponse } from '../services/analysisApi';

export interface PollingState {
    status: string;
    progress: number;
    startedAt: string | null;
    completedAt: string | null;
    result: AnalysisResponse | null;
    error: string | null;
    refresh: () => void;
}

export function useAnalysisPolling(analysisId: string | null, intervalMs = 2000): PollingState {
    const [state, setState] = useState<PollingState>({
        status: 'IDLE',
        progress: 0,
        startedAt: null,
        completedAt: null,
        result: null,
        error: null,
        refresh: () => {},
    });

    const refresh = useCallback(async () => {
        if (!analysisId) return;
        try {
            const data = await analysisApi.getAnalysis(analysisId);
            
            let progress = 0;
            if (data.status === 'QUEUED') progress = 10;
            if (data.status === 'RUNNING') progress = 50;
            if (data.status === 'COMPLETED' || data.status === 'FAILED') progress = 100;

            setState(prev => ({
                ...prev,
                status: data.status,
                progress,
                startedAt: data.created_at,
                completedAt: (data.status === 'COMPLETED' || data.status === 'FAILED') ? data.updated_at : null,
                result: data,
                error: null,
            }));
        } catch (err: any) {
            setState(prev => ({ ...prev, error: err.message || 'Failed to fetch analysis status' }));
        }
    }, [analysisId]);

    useEffect(() => {
        setState(prev => ({ ...prev, refresh }));
    }, [refresh]);

    useEffect(() => {
        if (!analysisId) return;

        // Initial fetch
        refresh();

        const terminalStates = ['COMPLETED', 'FAILED', 'NOT_FOUND'];

        const intervalId = setInterval(async () => {
            // Re-check state inside interval because closure might hold stale state 
            // but we don't want to poll if we already know it's terminal.
            // Actually, we can check the latest state.status using a ref, 
            // but for simplicity, we just fetch and stop the interval if terminal.
            if (!analysisId) return;
            try {
                const data = await analysisApi.getAnalysis(analysisId);
                
                let progress = 0;
                if (data.status === 'QUEUED') progress = 10;
                if (data.status === 'RUNNING') progress = 50;
                if (terminalStates.includes(data.status)) progress = 100;

                setState(prev => ({
                    ...prev,
                    status: data.status,
                    progress,
                    startedAt: data.created_at,
                    completedAt: terminalStates.includes(data.status) ? data.updated_at : null,
                    result: data,
                }));

                if (terminalStates.includes(data.status)) {
                    clearInterval(intervalId);
                }
            } catch (err: any) {
                setState(prev => ({ ...prev, error: err.message || 'Failed to fetch analysis status' }));
                clearInterval(intervalId); // Stop on error
            }
        }, intervalMs);

        return () => clearInterval(intervalId);
    }, [analysisId, intervalMs, refresh]);

    return state;
}
