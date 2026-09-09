'use client';
import { useState } from 'react';

export default function StockVisionPredictor() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [prediction, setPrediction] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) return;

    setLoading(true);
    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await fetch('http://localhost:8000/predict-chart', {
        method: 'POST',
        body: formData
      });
      const data = await response.json();
      if (data.status === 'success') {
        setPrediction(data);
      } else {
        alert(data.message);
      }
    } catch (err) {
      console.error('Prediction failed', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Stock Vision Predictor</h1>
      <form onSubmit={handleUpload} className="space-y-4">
        <input 
          type="file" 
          accept="png, jpg, jpeg" 
          onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
          className="block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-violet-50 file:text-violet-700 hover:file:bg-violet-100"
        />
        <button 
          type="submit" 
          disabled={loading}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? 'Analyzing Chart...' : 'Upload & Predict'}
        </button>
      </form>

      {prediction && (
        <div className="mt-6 p-4 bg-slate-50 rounded-lg border">
          <h2 className="font-semibold text-lg mb-2">Prediction Results</h2>
          <p>Historical Points Extracted: {prediction.historical_prices.length}</p>
          <p>Future Steps Projected: {prediction.predicted_prices.length}</p>
        </div>
      )}
    </div>
  );
}