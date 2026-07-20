import { useState, useEffect } from 'react';
import { analysisApi } from '../../services/analysisApi';

export function AIInsightsPanel({ analysisId }: { analysisId: string }) {
    const [data, setData] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchInsights = async () => {
            try {
                const res = await analysisApi.getInsights(analysisId);
                setData(res);
            } catch (err: any) {
                setError(err.message || "Failed to load AI insights");
            } finally {
                setLoading(false);
            }
        };
        fetchInsights();
    }, [analysisId]);

    if (loading) return <div className="p-6 bg-indigo-50 border border-indigo-100 rounded-lg shadow-sm animate-pulse h-40"></div>;
    if (error) return <div className="p-6 bg-red-50 text-red-600 rounded-lg">{error}</div>;
    if (!data) return null;

    return (
        <div className="mb-8 p-8 bg-gradient-to-br from-indigo-50 to-white rounded-lg border border-indigo-100 shadow-sm">
            <div className="flex items-center gap-3 mb-6">
                <div className="p-2 bg-indigo-600 text-white rounded-md">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
                </div>
                <h2 className="text-2xl font-bold text-slate-800">AI Analysis Insights</h2>
            </div>
            
            <p className="text-lg text-slate-700 font-medium mb-8 leading-relaxed">
                {data.summary}
            </p>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
                <div>
                    <h3 className="text-lg font-semibold text-green-800 mb-3 flex items-center gap-2">
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
                        Strengths
                    </h3>
                    <ul className="space-y-2">
                        {data.strengths.map((s: string, i: number) => (
                            <li key={i} className="text-slate-700 flex items-start gap-2">
                                <span className="text-green-500 mt-1">•</span> {s}
                            </li>
                        ))}
                    </ul>
                </div>
                <div>
                    <h3 className="text-lg font-semibold text-orange-800 mb-3 flex items-center gap-2">
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
                        Risks & Warnings
                    </h3>
                    <ul className="space-y-2">
                        {data.risks.map((r: string, i: number) => (
                            <li key={i} className="text-slate-700 flex items-start gap-2">
                                <span className="text-orange-500 mt-1">•</span> {r}
                            </li>
                        ))}
                        {data.risks.length === 0 && <li className="text-slate-500 italic">No major risks identified.</li>}
                    </ul>
                </div>
            </div>

            <hr className="border-indigo-100 my-6" />

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
                <div>
                    <h3 className="text-md font-bold text-slate-800 mb-2">Fairness Findings</h3>
                    <ul className="space-y-2">
                        {data.fairness_findings.map((f: string, i: number) => (
                            <li key={i} className="text-sm text-slate-600">{f}</li>
                        ))}
                    </ul>
                </div>
                <div>
                    <h3 className="text-md font-bold text-slate-800 mb-2">Explainability Findings</h3>
                    <ul className="space-y-2">
                        {data.explainability_findings.map((f: string, i: number) => (
                            <li key={i} className="text-sm text-slate-600">{f}</li>
                        ))}
                    </ul>
                </div>
            </div>

            <div className="bg-white p-5 rounded-md border border-indigo-100">
                <h3 className="text-sm font-bold text-slate-800 uppercase tracking-wider mb-3">AI Suggested Questions</h3>
                <div className="flex flex-wrap gap-2">
                    {data.follow_up_questions.map((q: string, i: number) => (
                        <button key={i} className="px-3 py-1.5 bg-indigo-50 text-indigo-700 hover:bg-indigo-100 text-sm rounded-full transition-colors">
                            {q}
                        </button>
                    ))}
                </div>
            </div>
        </div>
    );
}
