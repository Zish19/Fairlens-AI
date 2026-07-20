import { BrowserRouter, Routes, Route, Navigate, Link } from 'react-router-dom';
import { UploadPage } from './pages/UploadPage';
import { Datasets } from './pages/Datasets';
import { Analyses } from './pages/Analyses';
import { RunAnalysis } from './pages/RunAnalysis';
import { AnalysisDetail } from './pages/AnalysisDetail';

function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans">
      <header className="bg-white border-b border-slate-200 px-6 py-4 flex items-center justify-between">
        <h1 className="text-xl font-bold text-slate-900 tracking-tight">FairLens AI</h1>
        <nav className="flex items-center space-x-6">
          <Link to="/datasets" className="text-sm font-medium text-slate-600 hover:text-slate-900">Datasets</Link>
          <Link to="/analyses" className="text-sm font-medium text-slate-600 hover:text-slate-900">Analyses</Link>
          <Link to="/upload" className="text-sm font-medium text-blue-600 hover:text-blue-800">Upload Data</Link>
        </nav>
      </header>
      <main className="p-6">
        {children}
      </main>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Navigate to="/datasets" replace />} />
          <Route path="/upload" element={<UploadPage />} />
          <Route path="/datasets" element={<Datasets />} />
          <Route path="/datasets/:datasetId/versions/:versionId/analyze" element={<RunAnalysis />} />
          <Route path="/analyses" element={<Analyses />} />
          <Route path="/analyses/:analysisId" element={<AnalysisDetail />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}

export default App;
