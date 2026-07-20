import { useParams } from 'react-router-dom';
import { useAnalysisPolling } from '../hooks/useAnalysisPolling';
import { MetricGrid } from '../components/analysis/MetricGrid';
import { GroupComparisonChart } from '../components/analysis/GroupComparisonChart';
import { FeatureImportanceChart } from '../components/analysis/FeatureImportanceChart';
import { AIInsightsPanel } from '../components/analysis/AIInsightsPanel';

export function AnalysisDetail() {
    const { analysisId } = useParams();
    const { status, progress, result, error, startedAt, completedAt } = useAnalysisPolling(analysisId || null);

    if (error) {
        return (
            <div className="max-w-5xl mx-auto py-8">
                <div className="bg-red-50 text-red-700 p-4 rounded-md border border-red-200">
                    Failed to load analysis: {error}
                </div>
            </div>
        );
    }

    if (!result) {
        return (
            <div className="max-w-5xl mx-auto py-8">
                <div className="animate-pulse flex space-x-4">
                    <div className="flex-1 space-y-4 py-1">
                        <div className="h-4 bg-slate-200 rounded w-3/4"></div>
                        <div className="space-y-2">
                            <div className="h-4 bg-slate-200 rounded"></div>
                            <div className="h-4 bg-slate-200 rounded w-5/6"></div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    const isRunning = status === 'QUEUED' || status === 'RUNNING';

    return (
        <div className="max-w-5xl mx-auto py-8 space-y-8">
            {/* Overview Panel */}
            <section className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm flex justify-between items-center">
                <div>
                    <h1 className="text-2xl font-bold text-slate-900 mb-1">Analysis Details</h1>
                    <p className="text-sm text-slate-500">ID: {result.id}</p>
                </div>
                <div className="text-right">
                    <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                        status === 'COMPLETED' ? 'bg-green-100 text-green-800' :
                        status === 'FAILED' ? 'bg-red-100 text-red-800' :
                        'bg-blue-100 text-blue-800'
                    }`}>
                        {status}
                    </span>
                    {startedAt && (
                        <p className="text-xs text-slate-500 mt-2">
                            Started: {new Date(startedAt).toLocaleString()}
                        </p>
                    )}
                    {completedAt && (
                        <p className="text-xs text-slate-500 mt-1">
                            Completed: {new Date(completedAt).toLocaleString()}
                        </p>
                    )}
                </div>
            </section>

            {/* Timeline / Progress Panel */}
            {isRunning && (
                <section className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm" aria-live="polite">
                    <div className="mb-2 flex justify-between text-sm font-medium text-slate-700">
                        <span>Progress</span>
                        <span>{progress}%</span>
                    </div>
                    <div className="w-full bg-slate-200 rounded-full h-2.5">
                        <div className="bg-blue-600 h-2.5 rounded-full transition-all duration-500" style={{ width: `${progress}%` }}></div>
                    </div>
                    <p className="text-sm text-slate-500 mt-4 text-center animate-pulse">
                        Analyzing dataset, training model, and computing fairness metrics...
                    </p>
                </section>
            )}

            {/* Results */}
            {status === 'COMPLETED' && (
                <>
                    <AIInsightsPanel analysisId={result.id} />
                    
                    <MetricGrid metrics={result.metrics} />
                    <GroupComparisonChart metrics={result.metrics} />
                    <FeatureImportanceChart analysisId={result.id} />

                    {/* Interpretation Panel */}
                    <section className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm">
                        <h2 className="text-xl font-bold mb-4 text-slate-800">Interpretation</h2>
                        <div className="space-y-4">
                            {result.metrics.filter(m => m.interpretation && !m.subgroup).map(m => (
                                <div key={m.metric_name} className="flex gap-3">
                                    <div className="w-1 bg-blue-500 rounded-full"></div>
                                    <div>
                                        <h4 className="font-semibold text-slate-700">{m.metric_name}</h4>
                                        <p className="text-slate-600">{m.interpretation}</p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </section>

                    {/* Recommendation Panel */}
                    <section className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm">
                        <h2 className="text-xl font-bold mb-4 text-slate-800">Recommendations</h2>
                        {result.recommendations.length > 0 ? (
                            <div className="space-y-4">
                                {result.recommendations.map((rec, i) => (
                                    <div key={i} className={`p-4 rounded-md border ${rec.severity === 'warning' ? 'bg-orange-50 border-orange-200' : 'bg-blue-50 border-blue-200'}`}>
                                        <h4 className="font-semibold text-slate-800 mb-1">{rec.title}</h4>
                                        <p className="text-sm text-slate-700 mb-3">{rec.description}</p>
                                        <div className="inline-block bg-white px-3 py-2 rounded text-sm font-medium border border-slate-200">
                                            <span className="text-slate-500 uppercase text-xs mr-2 tracking-wider">Action</span>
                                            {rec.recommendedAction}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <p className="text-slate-500 italic">No recommendations available for this run.</p>
                        )}
                    </section>
                </>
            )}
        </div>
    );
}
