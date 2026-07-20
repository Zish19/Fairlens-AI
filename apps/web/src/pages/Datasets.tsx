import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';

interface Dataset {
    id: string;
    name: string;
    created_at: string;
    versions: any[];
}

export function Datasets() {
    const [datasets, setDatasets] = useState<Dataset[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchDatasets = async () => {
            try {
                const res = await axios.get('http://localhost:8000/api/v1/datasets');
                setDatasets(res.data.datasets);
            } catch (err) {
                console.error(err);
            }
            setLoading(false);
        };
        fetchDatasets();
    }, []);

    if (loading) return <div className="p-8">Loading datasets...</div>;

    return (
        <div className="max-w-5xl mx-auto py-8">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-2xl font-bold">Datasets</h1>
                <Link to="/upload" className="bg-blue-600 text-white px-4 py-2 rounded font-medium hover:bg-blue-700">
                    Upload New Dataset
                </Link>
            </div>
            
            <div className="bg-white rounded-lg border border-slate-200 overflow-hidden shadow-sm">
                <table className="w-full text-left text-sm">
                    <thead className="bg-slate-50 border-b border-slate-200 text-slate-600 uppercase">
                        <tr>
                            <th className="px-6 py-4 font-semibold">Name</th>
                            <th className="px-6 py-4 font-semibold">Versions</th>
                            <th className="px-6 py-4 font-semibold">Created</th>
                            <th className="px-6 py-4 font-semibold text-right">Actions</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                        {datasets.length === 0 ? (
                            <tr>
                                <td colSpan={4} className="px-6 py-8 text-center text-slate-500">
                                    No datasets found. Upload one to get started.
                                </td>
                            </tr>
                        ) : (
                            datasets.map(d => (
                                <tr key={d.id} className="hover:bg-slate-50">
                                    <td className="px-6 py-4 font-medium text-slate-900">{d.name}</td>
                                    <td className="px-6 py-4 text-slate-600">{d.versions.length}</td>
                                    <td className="px-6 py-4 text-slate-500">{new Date(d.created_at).toLocaleDateString()}</td>
                                    <td className="px-6 py-4 text-right">
                                        {d.versions.length > 0 && (
                                            <Link 
                                                to={`/datasets/${d.id}/versions/${d.versions[0].id}/analyze`}
                                                className="text-blue-600 hover:text-blue-800 font-medium"
                                            >
                                                Run Analysis
                                            </Link>
                                        )}
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
