'use client';
import { useState } from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine, Brush } from 'recharts';

export default function StockVisionPredictor() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [modelType, setModelType] = useState('random_walk');
  const [prediction, setPrediction] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) return;

    setLoading(true);
    setErrorMessage(null);
    setPrediction(null);

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('model_type', modelType);

    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${API_URL}/predict-chart`, {
        method: 'POST',
        body: formData,
      });
      
      const data = await response.json();
      if (!response.ok) throw new Error(data.message || 'Server error');

      if (data.status === 'success') {
        setPrediction(data);
      } else {
        setErrorMessage(data.message || 'Could not isolate chart line.');
      }
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to connect to backend server.');
    } finally {
      setLoading(false);
    }
  };

  const exportData = (format: 'json' | 'csv') => {
    if (!prediction) return;
    if (format === 'json') {
      const blob = new Blob([JSON.stringify(prediction, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'stock-prediction.json';
      a.click();
    } else {
      let csv = 'Index,Price,Type\n';
      prediction.historical_prices.forEach((p: number, i: number) => csv += `${i},${p},Historical\n`);
      prediction.predicted_prices.forEach((p: number, i: number) => csv += `${prediction.historical_prices.length + i},${p},Predicted\n`);
      const blob = new Blob([csv], { type: 'text/csv' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'stock-prediction.csv';
      a.click();
    }
  };

  const chartData = prediction ? [
    ...prediction.historical_prices.map((price: number, index: number) => ({
      index,
      Price: price,
      SMA: index >= 4 ? prediction.sma[index - 4] : null,
    })),
    ...prediction.predicted_prices.map((price: number, index: number) => ({
      index: prediction.historical_prices.length + index,
      Price: price,
      SMA: null,
    }))
  ] : [];

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100 flex flex-col items-center justify-center p-6">
      <div className="w-full max-w-4xl bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl p-8 space-y-6">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-emerald-400">Stock Vision Predictor</h1>
          <p className="text-slate-400 text-sm mt-1">Extract chart pixels, apply predictive algorithms, and analyze interactive timelines.</p>
        </div>

        <form onSubmit={handleUpload} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="border-2 border-dashed border-slate-700 hover:border-emerald-500 rounded-xl p-4 text-center bg-slate-950/50 cursor-pointer flex items-center justify-center">
              <input 
                type="file" 
                accept=".png, .jpg, .jpeg" 
                onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                className="w-full text-sm text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-emerald-500 file:text-slate-950 hover:file:bg-emerald-400 cursor-pointer"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1 uppercase tracking-wider">Forecasting Model</label>
              <select 
                value={modelType} 
                onChange={(e) => setModelType(e.target.value)}
                className="w-full bg-slate-950 border border-slate-700 rounded-xl p-3 text-sm text-slate-200 focus:outline-none focus:border-emerald-500"
              >
                <option value="random_walk">Random Walk Simulation</option>
                <option value="linear">Linear Trend Regression</option>
                <option value="exponential">Exponential Growth Smoothing</option>
              </select>
            </div>
          </div>

          <button 
            type="submit" 
            disabled={loading || !selectedFile}
            className="w-full py-3 px-4 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold rounded-xl transition disabled:opacity-50 shadow-lg shadow-emerald-500/10 cursor-pointer"
          >
            {loading ? 'Analyzing Chart Pixels...' : 'Run Advanced Vision Prediction'}
          </button>
        </form>

        {errorMessage && (
          <div className="p-4 bg-red-950/50 border border-red-800 rounded-xl text-red-300 text-sm">
            {errorMessage}
          </div>
        )}

        {prediction && (
          <div className="mt-6 p-5 bg-slate-950 rounded-xl border border-slate-800 space-y-4">
            <div className="flex justify-between items-center">
              <h2 className="font-bold text-lg text-emerald-400">Interactive Analysis Dashboard</h2>
              <div className="flex gap-2">
                <button onClick={() => exportData('json')} className="px-3 py-1 bg-slate-800 hover:bg-slate-700 text-xs font-medium rounded-lg text-slate-200">Export JSON</button>
                <button onClick={() => exportData('csv')} className="px-3 py-1 bg-slate-800 hover:bg-slate-700 text-xs font-medium rounded-lg text-slate-200">Export CSV</button>
              </div>
            </div>

            <div className="w-full h-80">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData}>
                  <XAxis dataKey="index" stroke="#64748b" />
                  <YAxis stroke="#64748b" domain={['auto', 'auto']} />
                  <Tooltip contentStyle={{ backgroundColor: '#020617', borderColor: '#334155', borderRadius: '0.5rem', color: '#f8fafc' }} />
                  <ReferenceLine x={prediction.historical_prices.length} stroke="#f97316" strokeDasharray="3 3" />
                  <Line type="monotone" dataKey="Price" stroke="#10b981" strokeWidth={2} dot={false} name="Extracted Price" />
                  <Line type="monotone" dataKey="SMA" stroke="#38bdf8" strokeWidth={1.5} dot={false} name="5-Period SMA" />
                  <Brush dataKey="index" height={30} stroke="#334155" fill="#0f172a" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}