import type { MetricResultResponse } from '../../services/analysisApi';

export function MetricCard({ metric }: { metric: MetricResultResponse }) {
    // Basic interpretation of values
    const isWarning = Math.abs(metric.metric_value) > 0.1;
    
    return (
        <div className={`p-6 rounded-lg border ${isWarning ? 'bg-orange-50 border-orange-200' : 'bg-white border-slate-200'} shadow-sm`}>
            <div className="flex justify-between items-start mb-4">
                <h3 className="text-sm font-semibold text-slate-700 uppercase tracking-wider">{metric.metric_name}</h3>
                {isWarning ? (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
                        Warning
                    </span>
                ) : (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        Acceptable
                    </span>
                )}
            </div>
            
            <div className="mb-2">
                <span className="text-3xl font-bold text-slate-900">
                    {metric.metric_value.toFixed(4)}
                </span>
            </div>
            
            <p className="text-sm text-slate-600 mb-2">
                Threshold: [-0.1, 0.1]
            </p>

            {metric.interpretation && (
                <p className="text-sm text-slate-700 bg-white/50 p-3 rounded mt-4 text-balance">
                    {metric.interpretation}
                </p>
            )}
        </div>
    );
}

export function MetricGrid({ metrics }: { metrics: MetricResultResponse[] }) {
    // Only show top-level difference metrics as cards, not subgroup rates
    const cards = metrics.filter(m => m.metric_name.includes('Difference') || m.metric_name === 'DisparateImpact');

    if (cards.length === 0) return null;

    return (
        <div className="mb-8">
            <h2 className="text-xl font-bold mb-4 text-slate-800">Fairness Score Cards</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {cards.map(m => (
                    <MetricCard key={m.metric_name} metric={m} />
                ))}
            </div>
        </div>
    );
}
