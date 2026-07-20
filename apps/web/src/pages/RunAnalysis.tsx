import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { analysisApi } from '../services/analysisApi';
import type { AnalysisConfig } from '../services/analysisApi';

export function RunAnalysis() {
    const { datasetId, versionId } = useParams();
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const [config, setConfig] = useState<AnalysisConfig>({
        schema_version: 1,
        training: {
            algorithm: 'RandomForestClassifier',
            random_state: 42,
            test_size: 0.2
        },
        fairness: {
            target_column: '',
            sensitive_attribute: '',
            positive_label: '1',
            metrics: ['DemographicParity', 'EqualOpportunity']
        }
    });

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!versionId) return;
        setLoading(true);
        setError(null);
        try {
            const result = await analysisApi.submitAnalysis(versionId, config);
            navigate(`/analyses/${result.id}`);
        } catch (err: any) {
            setError(err.response?.data?.detail || err.message);
            setLoading(false);
        }
    };

    return (
        <div className="max-w-3xl mx-auto py-8">
            <h1 className="text-3xl font-bold mb-8">Run New Analysis</h1>
            
            {error && (
                <div className="bg-red-50 text-red-700 p-4 rounded-md mb-6 border border-red-200">
                    {error}
                </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-8 bg-white p-8 rounded-lg shadow-sm border border-slate-200">
                
                {/* Dataset Section (Read-only) */}
                <section>
                    <h2 className="text-xl font-semibold mb-4">Dataset Configuration</h2>
                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-1">Dataset ID</label>
                            <input type="text" disabled value={datasetId} className="w-full p-2 border border-slate-300 rounded-md bg-slate-50 text-slate-500" />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-1">Version ID</label>
                            <input type="text" disabled value={versionId} className="w-full p-2 border border-slate-300 rounded-md bg-slate-50 text-slate-500" />
                        </div>
                    </div>
                </section>

                <hr className="border-slate-200" />

                {/* Training Section */}
                <section>
                    <h2 className="text-xl font-semibold mb-4">Training Configuration</h2>
                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label htmlFor="algorithm" className="block text-sm font-medium text-slate-700 mb-1">Algorithm</label>
                            <select 
                                id="algorithm"
                                value={config.training.algorithm} 
                                onChange={e => setConfig({...config, training: {...config.training, algorithm: e.target.value}})}
                                className="w-full p-2 border border-slate-300 rounded-md focus:ring-2 focus:ring-blue-500"
                            >
                                <option value="RandomForestClassifier">Random Forest</option>
                            </select>
                        </div>
                        <div>
                            <label htmlFor="test_size" className="block text-sm font-medium text-slate-700 mb-1">Test Split Size</label>
                            <input 
                                id="test_size"
                                type="number" step="0.01" min="0.1" max="0.5" 
                                value={config.training.test_size} 
                                onChange={e => setConfig({...config, training: {...config.training, test_size: parseFloat(e.target.value)}})}
                                className="w-full p-2 border border-slate-300 rounded-md focus:ring-2 focus:ring-blue-500" 
                            />
                        </div>
                    </div>
                </section>

                <hr className="border-slate-200" />

                {/* Fairness Section */}
                <section>
                    <h2 className="text-xl font-semibold mb-4">Fairness Configuration</h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label htmlFor="target_column" className="block text-sm font-medium text-slate-700 mb-1">Target Column</label>
                            <input 
                                id="target_column"
                                type="text" required
                                placeholder="e.g. income"
                                value={config.fairness.target_column}
                                onChange={e => setConfig({...config, fairness: {...config.fairness, target_column: e.target.value}})}
                                className="w-full p-2 border border-slate-300 rounded-md focus:ring-2 focus:ring-blue-500" 
                            />
                        </div>
                        <div>
                            <label htmlFor="positive_label" className="block text-sm font-medium text-slate-700 mb-1">Positive Label</label>
                            <input 
                                id="positive_label"
                                type="text" required
                                placeholder="e.g. >50K"
                                value={config.fairness.positive_label}
                                onChange={e => setConfig({...config, fairness: {...config.fairness, positive_label: e.target.value}})}
                                className="w-full p-2 border border-slate-300 rounded-md focus:ring-2 focus:ring-blue-500" 
                            />
                        </div>
                        <div className="md:col-span-2">
                            <label htmlFor="sensitive_attribute" className="block text-sm font-medium text-slate-700 mb-1">Sensitive Attribute</label>
                            <input 
                                id="sensitive_attribute"
                                type="text" required
                                placeholder="e.g. sex or race"
                                value={config.fairness.sensitive_attribute}
                                onChange={e => setConfig({...config, fairness: {...config.fairness, sensitive_attribute: e.target.value}})}
                                className="w-full p-2 border border-slate-300 rounded-md focus:ring-2 focus:ring-blue-500" 
                            />
                        </div>
                    </div>
                </section>

                {/* Submit Section */}
                <div className="pt-4">
                    <button 
                        type="submit" 
                        disabled={loading}
                        className="w-full bg-blue-600 text-white font-semibold py-3 rounded-md hover:bg-blue-700 disabled:opacity-50 transition-colors"
                    >
                        {loading ? 'Starting Analysis...' : 'Run Analysis'}
                    </button>
                </div>
            </form>
        </div>
    );
}
