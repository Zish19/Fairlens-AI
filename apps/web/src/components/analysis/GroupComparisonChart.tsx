import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import type { MetricResultResponse } from '../../services/analysisApi';

export function GroupComparisonChart({ metrics }: { metrics: MetricResultResponse[] }) {
    // Extract SelectionRate for subgroups
    const subgroupRates = metrics.filter(m => m.metric_name === 'SelectionRate' && m.subgroup);

    if (subgroupRates.length === 0) return null;

    const data = subgroupRates.map(m => ({
        group: m.subgroup,
        rate: m.metric_value
    }));

    // Textual summary for accessibility
    const summaryText = data.map(d => `${d.group} has a selection rate of ${d.rate.toFixed(4)}.`).join(' ');

    return (
        <div className="mb-8 p-6 bg-white rounded-lg border border-slate-200 shadow-sm">
            <h2 className="text-xl font-bold mb-6 text-slate-800">Group Comparison (Selection Rate)</h2>
            
            <div className="h-80 w-full mb-6">
                <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                        data={data}
                        margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                        accessibilityLayer
                    >
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                        <XAxis dataKey="group" axisLine={false} tickLine={false} tick={{fill: '#64748b'}} />
                        <YAxis axisLine={false} tickLine={false} tick={{fill: '#64748b'}} />
                        <Tooltip 
                            cursor={{fill: '#f1f5f9'}}
                            contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                        />
                        <Legend wrapperStyle={{ paddingTop: '20px' }} />
                        <Bar dataKey="rate" name="Selection Rate" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                    </BarChart>
                </ResponsiveContainer>
            </div>

            <div className="bg-slate-50 p-4 rounded-md border border-slate-200">
                <h4 className="text-sm font-semibold text-slate-700 mb-1">Chart Summary (Accessibility)</h4>
                <p className="text-sm text-slate-600">{summaryText}</p>
            </div>
        </div>
    );
}
