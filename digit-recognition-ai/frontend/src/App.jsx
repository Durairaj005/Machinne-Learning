import React, { useEffect, useMemo, useRef, useState } from 'react';
import html2canvas from 'html2canvas';
import { jsPDF } from 'jspdf';
import {
  FiActivity,
  FiBarChart2,
  FiCheckCircle,
  FiCpu,
  FiEdit3,
  FiGrid,
  FiMoon,
  FiSun,
  FiTrash2,
  FiVolume2,
  FiVolumeX,
  FiZap,
} from 'react-icons/fi';

import AnimatedBackground from './components/AnimatedBackground';
import InputStudio from './components/InputStudio';
import PredictionCard from './components/PredictionCard';
import MetricsSection from './components/MetricsSection';
import { api, resolveAssetUrl } from './api/client';

function formatHistoryItem(result, source) {
  return {
    id: crypto.randomUUID(),
    digit: result.predicted_digit,
    confidence: Number(result.confidence).toFixed(1),
    source,
    time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
  };
}

function playPredictionTone() {
  try {
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    if (!AudioContext) return;
    const ctx = new AudioContext();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(880, ctx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(1320, ctx.currentTime + 0.08);
    gain.gain.setValueAtTime(0.04, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 0.2);
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start();
    osc.stop(ctx.currentTime + 0.22);
  } catch (e) {
    // Ignore audio autoplay restrictions
  }
}

export default function App() {
  const predictionCardRef = useRef(null);
  const previewUrlRef = useRef('');

  const [activeView, setActiveView] = useState('studio'); // 'studio' | 'analytics' | 'unified'
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [history, setHistory] = useState([]);
  const [health, setHealth] = useState('checking');
  const [darkMode, setDarkMode] = useState(true);
  const [soundEnabled, setSoundEnabled] = useState(true);

  const modelReady = health === 'ready';

  useEffect(() => {
    const stored = window.localStorage.getItem('digit-history');
    if (stored) {
      try {
        setHistory(JSON.parse(stored));
      } catch (e) {}
    }
  }, []);

  useEffect(() => () => {
    if (previewUrlRef.current) {
      URL.revokeObjectURL(previewUrlRef.current);
    }
  }, []);

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const [healthRes, metricsRes] = await Promise.all([
          api.get('/health'),
          api.get('/metrics'),
        ]);
        setHealth(healthRes.data.model_ready ? 'ready' : 'not trained');
        setMetrics(metricsRes.data);
      } catch (err) {
        setHealth('offline');
      }
    };
    fetchDashboard();
  }, []);

  const assetUrls = useMemo(
    () => ({
      training_curves: resolveAssetUrl(metrics?.artifacts?.training_curves),
      confusion_matrix: resolveAssetUrl(metrics?.artifacts?.confusion_matrix),
      sample_predictions: resolveAssetUrl(metrics?.artifacts?.sample_predictions),
    }),
    [metrics],
  );

  const handleFileSelect = (selectedFile) => {
    setError('');
    setFile(selectedFile);
    setResult(null);

    if (previewUrlRef.current) {
      URL.revokeObjectURL(previewUrlRef.current);
    }
    const objectUrl = URL.createObjectURL(selectedFile);
    previewUrlRef.current = objectUrl;
    setPreview(objectUrl);
  };

  const clearUpload = (message = '') => {
    if (previewUrlRef.current) {
      URL.revokeObjectURL(previewUrlRef.current);
      previewUrlRef.current = '';
    }
    setFile(null);
    setPreview('');
    setResult(null);
    setError(message);
  };

  const runPrediction = async (overrideDataUrl, sourceLabel = 'Canvas drawing') => {
    try {
      if (!modelReady) {
        throw new Error('Model is not ready yet. Please train the model.');
      }

      setLoading(true);
      setError('');

      const formData = new FormData();
      if (overrideDataUrl) {
        const blob = await fetch(overrideDataUrl).then((r) => r.blob());
        formData.append('file', blob, 'canvas.png');
      } else if (file) {
        formData.append('file', file);
      } else {
        throw new Error('Please draw on the canvas or upload an image first.');
      }

      const response = await api.post('/predict', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      const nextResult = response.data;
      setResult(nextResult);

      if (soundEnabled) {
        playPredictionTone();
      }

      setHistory((curr) => {
        const updated = [formatHistoryItem(nextResult, sourceLabel), ...curr].slice(0, 10);
        window.localStorage.setItem('digit-history', JSON.stringify(updated));
        return updated;
      });
    } catch (err) {
      setError(err?.response?.data?.detail || err.message || 'Prediction failed.');
    } finally {
      setLoading(false);
    }
  };

  const clearHistory = () => {
    setHistory([]);
    window.localStorage.removeItem('digit-history');
  };

  const downloadPredictionImage = async () => {
    if (!predictionCardRef.current) return;
    const canvas = await html2canvas(predictionCardRef.current, { backgroundColor: null, scale: 2 });
    const link = document.createElement('a');
    link.download = `digit-${result?.predicted_digit ?? 'prediction'}.png`;
    link.href = canvas.toDataURL('image/png');
    link.click();
  };

  const downloadPredictionPdf = async () => {
    if (!predictionCardRef.current) return;
    const canvas = await html2canvas(predictionCardRef.current, { backgroundColor: null, scale: 2 });
    const image = canvas.toDataURL('image/png');
    const pdf = new jsPDF({ orientation: 'p', unit: 'px', format: [canvas.width, canvas.height] });
    pdf.addImage(image, 'PNG', 0, 0, canvas.width, canvas.height);
    pdf.save(`digit-${result?.predicted_digit ?? 'prediction'}.pdf`);
  };

  return (
    <div className={`relative min-h-screen ${darkMode ? 'bg-[#030712] text-white' : 'bg-slate-100 text-slate-900'}`}>
      <AnimatedBackground />

      <div className="relative mx-auto flex w-full max-w-[1300px] flex-col gap-5 px-4 py-5 sm:px-6">
        {/* Navigation Bar */}
        <header className="glass-card flex flex-wrap items-center justify-between gap-4 rounded-2xl px-5 py-3.5 shadow-glow">
          {/* Logo & Brand */}
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-cyan-400 to-fuchsia-500 text-lg font-black text-slate-950 shadow-[0_0_20px_rgba(34,211,238,0.4)]">
              AI
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-lg font-black tracking-tight text-white">DigitSense AI</h1>
                <span className="rounded-md border border-cyan-400/30 bg-cyan-400/10 px-2 py-0.5 text-[10px] font-bold text-cyan-300">
                  CNN v1.0
                </span>
              </div>
              <p className="text-[11px] text-slate-400">Handwritten Digit Recognition System</p>
            </div>
          </div>

          {/* Center Navigation Tabs */}
          <div className="flex items-center gap-1 rounded-xl bg-white/5 p-1 text-xs">
            <button
              type="button"
              onClick={() => setActiveView('studio')}
              className={`inline-flex items-center gap-1.5 rounded-lg px-3.5 py-1.5 font-semibold transition ${
                activeView === 'studio'
                  ? 'bg-gradient-to-r from-cyan-400 to-sky-500 text-slate-950 shadow-md'
                  : 'text-slate-300 hover:text-white'
              }`}
            >
              <FiEdit3 /> Studio
            </button>
            <button
              type="button"
              onClick={() => setActiveView('analytics')}
              className={`inline-flex items-center gap-1.5 rounded-lg px-3.5 py-1.5 font-semibold transition ${
                activeView === 'analytics'
                  ? 'bg-gradient-to-r from-cyan-400 to-sky-500 text-slate-950 shadow-md'
                  : 'text-slate-300 hover:text-white'
              }`}
            >
              <FiBarChart2 /> Analytics
            </button>
            <button
              type="button"
              onClick={() => setActiveView('unified')}
              className={`inline-flex items-center gap-1.5 rounded-lg px-3.5 py-1.5 font-semibold transition ${
                activeView === 'unified'
                  ? 'bg-gradient-to-r from-cyan-400 to-sky-500 text-slate-950 shadow-md'
                  : 'text-slate-300 hover:text-white'
              }`}
            >
              <FiGrid /> Unified View
            </button>
          </div>

          {/* Right Utility Buttons */}
          <div className="flex items-center gap-2">
            {/* Model Status Pill */}
            <div className="inline-flex items-center gap-1.5 rounded-full border border-emerald-400/25 bg-emerald-400/10 px-3 py-1 text-xs font-semibold text-emerald-300">
              <span className="h-2 w-2 animate-pulse rounded-full bg-emerald-400" />
              <span>{modelReady ? 'Online (98.78% Acc)' : health}</span>
            </div>

            {/* Sound Toggle */}
            <button
              type="button"
              onClick={() => setSoundEnabled((v) => !v)}
              className="flex h-9 w-9 items-center justify-center rounded-xl border border-white/10 bg-white/5 text-slate-300 transition hover:bg-white/10"
              title={soundEnabled ? 'Mute sound' : 'Enable sound'}
            >
              {soundEnabled ? <FiVolume2 className="text-cyan-300" /> : <FiVolumeX className="text-slate-500" />}
            </button>

            {/* Theme Toggle */}
            <button
              type="button"
              onClick={() => setDarkMode((v) => !v)}
              className="flex h-9 w-9 items-center justify-center rounded-xl border border-white/10 bg-white/5 text-slate-300 transition hover:bg-white/10"
              title="Toggle theme"
            >
              {darkMode ? <FiSun className="text-amber-300" /> : <FiMoon className="text-slate-300" />}
            </button>
          </div>
        </header>

        {/* Studio View: Side-by-Side Drawing & Live Prediction */}
        {(activeView === 'studio' || activeView === 'unified') && (
          <div className="space-y-4">
            <div className="grid gap-5 lg:grid-cols-2">
              {/* Left Column: Input Studio (Canvas & Upload) */}
              <InputStudio
                preview={preview}
                fileName={file?.name || ''}
                loading={loading}
                modelReady={modelReady}
                onFileSelect={handleFileSelect}
                onPredictUpload={() => runPrediction(undefined, 'Uploaded image')}
                onPredictCanvas={(dataUrl) => runPrediction(dataUrl, 'Canvas drawing')}
                onClearUpload={clearUpload}
                error={error}
              />

              {/* Right Column: Instant Live Prediction Card */}
              <PredictionCard
                ref={predictionCardRef}
                result={result}
                loading={loading}
                onDownloadImage={downloadPredictionImage}
                onDownloadPdf={downloadPredictionPdf}
              />
            </div>

            {/* Compact History Strip */}
            {history.length > 0 && (
              <div className="glass-card flex items-center justify-between gap-3 rounded-2xl px-4 py-2.5 shadow-glow">
                <div className="flex items-center gap-2 overflow-x-auto py-1">
                  <span className="whitespace-nowrap text-[11px] font-semibold text-slate-400">Recent:</span>
                  {history.slice(0, 6).map((item) => (
                    <div
                      key={item.id}
                      className="flex items-center gap-1.5 whitespace-nowrap rounded-lg border border-white/10 bg-white/5 px-2.5 py-1 text-xs"
                    >
                      <span className="font-bold text-white">Digit {item.digit}</span>
                      <span className="text-[10px] text-cyan-300">{item.confidence}%</span>
                      <span className="text-[9px] text-slate-500">({item.source.split(' ')[0]})</span>
                    </div>
                  ))}
                </div>

                <button
                  type="button"
                  onClick={clearHistory}
                  className="flex items-center gap-1 whitespace-nowrap text-[11px] text-slate-400 transition hover:text-rose-300"
                  title="Clear history"
                >
                  <FiTrash2 className="text-xs" /> Clear
                </button>
              </div>
            )}
          </div>
        )}

        {/* Analytics & Visualizations View */}
        {(activeView === 'analytics' || activeView === 'unified') && (
          <div className="space-y-4">
            <MetricsSection metrics={metrics} assetUrls={assetUrls} />
          </div>
        )}
      </div>
    </div>
  );
}