import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { analysisApi } from '../services/analysisApi';
import type { AnalysisResponse } from '../services/analysisApi';

export function Analyses() {
    const [analyses, setAnalyses] = useState<AnalysisResponse[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchAnalyses = async () => {
            try {
                const data = await analysisApi.listAnalyses();
                setAnalyses(data);
            } catch (err) {
                console.error(err);
            }
            setLoading(false);
        };
        fetchAnalyses();
    }, []);

    if (loading) return <div className="p-8">Loading analyses...</div>;

    return (
        <div className="max-w-5xl mx-auto py-8">
            <h1 className="text-2xl font-bold mb-6">Analysis History</h1>
            
            <div className="bg-white rounded-lg border border-slate-200 overflow-hidden shadow-sm">
                <table className="w-full text-left text-sm">
                    <thead className="bg-slate-50 border-b border-slate-200 text-slate-600 uppercase">
                        <tr>
                            <th className="px-6 py-4 font-semibold">ID</th>
                            <th className="px-6 py-4 font-semibold">Status</th>
                            <th className="px-6 py-4 font-semibold">Target / Sensitive</th>
                            <th className="px-6 py-4 font-semibold">Created</th>
                            <th className="px-6 py-4 font-semibold text-right">Actions</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                        {analyses.length === 0 ? (
                            <tr>
                                <td colSpan={5} className="px-6 py-8 text-center text-slate-500">
                                    No analyses found. Run an analysis on a dataset to see it here.
                                </td>
                            </tr>
                        ) : (
                            analyses.map(a => (
                                <tr key={a.id} className="hover:bg-slate-50">
                                    <td className="px-6 py-4 font-medium text-slate-900 font-mono text-xs">
                                        {a.id.substring(0, 8)}...
                                    </td>
                                    <td className="px-6 py-4">
                                        <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                                            a.status === 'COMPLETED' ? 'bg-green-100 text-green-800' :
                                            a.status === 'FAILED' ? 'bg-red-100 text-red-800' :
                                            'bg-blue-100 text-blue-800'
                                        }`}>
                                            {a.status}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 text-slate-600">
                                        <span className="font-semibold">{a.config.fairness.target_column}</span> / {a.config.fairness.sensitive_attribute}
                                    </td>
                                    <td className="px-6 py-4 text-slate-500">
                                        {new Date(a.created_at).toLocaleString()}
                                    </td>
                                    <td className="px-6 py-4 text-right">
                                        <Link 
                                            to={`/analyses/${a.id}`}
                                            className="text-blue-600 hover:text-blue-800 font-medium"
                                        >
                                            View Report
                                        </Link>
                                    </td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
