import { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { analysisApi } from '../../services/analysisApi';

export function FeatureImportanceChart({ analysisId }: { analysisId: string }) {
    const [data, setData] = useState<any[]>([]);
    const [expanded, setExpanded] = useState(false);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchFI = async () => {
            try {
                const res = await analysisApi.getExplainability(analysisId);
                setData(res.feature_importance || []);
            } catch (err: any) {
                setError(err.message || "Failed to load explainability");
            } finally {
                setLoading(false);
            }
        };
        fetchFI();
    }, [analysisId]);

    if (loading) return <div className="p-6 bg-white rounded-lg border border-slate-200 shadow-sm animate-pulse h-64"></div>;
    if (error) return <div className="p-6 bg-red-50 text-red-600 rounded-lg">{error}</div>;
    if (data.length === 0) return null;

    const limit = expanded ? 20 : 10;
    const displayData = data.slice(0, limit);

    const summaryText = displayData.map(d => `${d.feature} (importance: ${d.importance.toFixed(4)})`).join(', ');

    return (
        <div className="mb-8 p-6 bg-white rounded-lg border border-slate-200 shadow-sm">
            <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-bold text-slate-800">Global Feature Importance (SHAP)</h2>
                {data.length > 10 && (
                    <button 
                        onClick={() => setExpanded(!expanded)}
                        className="text-sm font-medium text-blue-600 hover:text-blue-800"
                    >
                        {expanded ? 'Show Top 10' : 'Show Top 20'}
                    </button>
                )}
            </div>
            
            <div className="h-96 w-full mb-6">
                <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                        data={displayData}
                        layout="vertical"
                        margin={{ top: 5, right: 30, left: 100, bottom: 5 }}
                        accessibilityLayer
                    >
                        <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#e2e8f0" />
                        <XAxis type="number" axisLine={false} tickLine={false} tick={{fill: '#64748b'}} />
                        <YAxis type="category" dataKey="feature" axisLine={false} tickLine={false} tick={{fill: '#64748b'}} width={120} />
                        <Tooltip 
                            cursor={{fill: '#f1f5f9'}}
                            contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                            formatter={(value: number) => value.toFixed(4)}
                        />
                        <Bar dataKey="importance" name="Mean |SHAP|" fill="#8b5cf6" radius={[0, 4, 4, 0]} />
                    </BarChart>
                </ResponsiveContainer>
            </div>

            <div className="bg-slate-50 p-4 rounded-md border border-slate-200">
                <h4 className="text-sm font-semibold text-slate-700 mb-1">Chart Summary (Accessibility)</h4>
                <p className="text-sm text-slate-600">Top features by importance: {summaryText}.</p>
            </div>
        </div>
    );
}
