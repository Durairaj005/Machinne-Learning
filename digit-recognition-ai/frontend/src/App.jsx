import React, { useEffect, useMemo, useRef, useState } from 'react';
import { motion } from 'framer-motion';
import html2canvas from 'html2canvas';
import { FiCpu, FiMoon, FiSun, FiZap } from 'react-icons/fi';
import { jsPDF } from 'jspdf';

import AnimatedBackground from './components/AnimatedBackground';
import DrawingCanvas from './components/DrawingCanvas';
import HistoryPanel from './components/HistoryPanel';
import MetricsSection from './components/MetricsSection';
import PredictionCard from './components/PredictionCard';
import Sidebar from './components/Sidebar';
import UploadPanel from './components/UploadPanel';
import { api, resolveAssetUrl } from './api/client';

const TYPE_LINES = [
  'Futuristic handwritten digit intelligence with a premium SaaS-grade experience.',
  'Upload a JPG image or sketch a digit to see the CNN prediction in real time.',
  'Designed as a polished local website demo with a clean REST API.',
];

function useTypewriter(lines) {
  const [index, setIndex] = useState(0);
  const [text, setText] = useState('');

  useEffect(() => {
    const current = lines[index % lines.length];
    let offset = 0;
    setText('');

    const interval = window.setInterval(() => {
      offset += 1;
      setText(current.slice(0, offset));
      if (offset >= current.length) {
        window.clearInterval(interval);
      }
    }, 28);

    const timeout = window.setTimeout(() => setIndex((value) => value + 1), current.length * 28 + 1800);

    return () => {
      window.clearInterval(interval);
      window.clearTimeout(timeout);
    };
  }, [index, lines]);

  return text;
}

function formatHistoryItem(result, source) {
  return {
    id: crypto.randomUUID(),
    digit: result.predicted_digit,
    confidence: result.confidence.toFixed(2),
    source,
    time: new Date().toLocaleString(),
  };
}

function playPredictionTone() {
  const AudioContext = window.AudioContext || window.webkitAudioContext;
  if (!AudioContext) return;
  const context = new AudioContext();
  const oscillator = context.createOscillator();
  const gainNode = context.createGain();
  oscillator.type = 'sine';
  oscillator.frequency.value = 880;
  gainNode.gain.value = 0.03;
  oscillator.connect(gainNode);
  gainNode.connect(context.destination);
  oscillator.start();
  oscillator.frequency.exponentialRampToValueAtTime(1320, context.currentTime + 0.08);
  gainNode.gain.exponentialRampToValueAtTime(0.0001, context.currentTime + 0.2);
  oscillator.stop(context.currentTime + 0.22);
}

export default function App() {
  const predictionCardRef = useRef(null);
  const previewUrlRef = useRef('');
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [history, setHistory] = useState([]);
  const [health, setHealth] = useState('checking');
  const [darkMode, setDarkMode] = useState(true);

  const typedText = useTypewriter(TYPE_LINES);
  const modelReady = health === 'ready';

  useEffect(() => {
    const stored = window.localStorage.getItem('digit-history');
    if (stored) {
      setHistory(JSON.parse(stored));
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
        const [healthResponse, metricsResponse] = await Promise.all([api.get('/health'), api.get('/metrics')]);
        setHealth(healthResponse.data.model_ready ? 'ready' : 'not trained');
        setMetrics(metricsResponse.data);
      } catch (requestError) {
        setHealth('offline');
      }
    };

    fetchDashboard();
  }, []);

  const assetUrls = useMemo(() => ({
    training_curves: resolveAssetUrl(metrics?.artifacts?.training_curves),
    confusion_matrix: resolveAssetUrl(metrics?.artifacts?.confusion_matrix),
    sample_predictions: resolveAssetUrl(metrics?.artifacts?.sample_predictions),
  }), [metrics]);

  const saveHistory = (nextHistory) => {
    setHistory(nextHistory);
    window.localStorage.setItem('digit-history', JSON.stringify(nextHistory));
  };

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

  const runPrediction = async (overrideDataUrl, sourceLabel = 'Uploaded image') => {
    try {
      if (!modelReady) {
        throw new Error('Train the backend model first. Run python train_model.py after placing the digit folders in dataset/0 to dataset/9.');
      }

      setLoading(true);
      setError('');

      const formData = new FormData();

      if (overrideDataUrl) {
        const blob = await fetch(overrideDataUrl).then((response) => response.blob());
        formData.append('file', blob, 'canvas.png');
      } else if (file) {
        formData.append('file', file);
      } else {
        throw new Error('Please upload an image or draw on the canvas first.');
      }

      const response = await api.post('/predict', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      const nextResult = response.data;
      setResult(nextResult);
      playPredictionTone();

      setHistory((currentHistory) => {
        const nextHistory = [formatHistoryItem(nextResult, sourceLabel), ...currentHistory].slice(0, 10);
        window.localStorage.setItem('digit-history', JSON.stringify(nextHistory));
        return nextHistory;
      });
    } catch (requestError) {
      setError(requestError?.response?.data?.detail || requestError.message || 'Prediction failed.');
    } finally {
      setLoading(false);
    }
  };

  const clearHistory = () => saveHistory([]);

  const downloadPredictionImage = async () => {
    if (!predictionCardRef.current) return;
    const canvas = await html2canvas(predictionCardRef.current, { backgroundColor: null, scale: 2 });
    const link = document.createElement('a');
    link.download = 'digit-prediction.png';
    link.href = canvas.toDataURL('image/png');
    link.click();
  };

  const downloadPredictionPdf = async () => {
    if (!predictionCardRef.current) return;
    const canvas = await html2canvas(predictionCardRef.current, { backgroundColor: null, scale: 2 });
    const image = canvas.toDataURL('image/png');
    const pdf = new jsPDF({ orientation: 'p', unit: 'px', format: [canvas.width, canvas.height] });
    pdf.addImage(image, 'PNG', 0, 0, canvas.width, canvas.height);
    pdf.save('digit-prediction.pdf');
  };

  const stats = useMemo(() => [
    { label: 'API Status', value: health === 'ready' ? 'Online' : health === 'offline' ? 'Offline' : 'Checking' },
    { label: 'Classes', value: '10 digits' },
    { label: 'Target', value: '95%+' },
    { label: 'Input', value: 'JPG / PNG' },
  ], [health]);

  return (
    <div className={`relative min-h-screen overflow-hidden ${darkMode ? 'bg-[#020617] text-white' : 'bg-slate-50 text-slate-900'}`}>
      <AnimatedBackground />

      <div className="relative mx-auto flex w-full max-w-[1600px] gap-6 px-4 py-6 sm:px-6 lg:px-8">
        <div className="hidden xl:block xl:w-[340px]">
          <Sidebar modelReady={modelReady} apiStatus={health} />
        </div>

        <main className="flex-1 space-y-6">
          <motion.section
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.65 }}
            className="glass-card rounded-[34px] p-6 shadow-glow md:p-8"
          >
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div className="max-w-4xl">
                <div className="inline-flex items-center gap-2 rounded-full border border-cyan-300/20 bg-cyan-300/10 px-4 py-2 text-xs font-semibold uppercase tracking-[0.28em] text-cyan-100">
                  <FiCpu /> AI Handwritten Digit Recognition System
                </div>
                <h1 className="mt-5 text-4xl font-black leading-tight text-white sm:text-5xl lg:text-6xl">
                  <span className="gradient-text">Predict handwritten digits</span> with a futuristic neural dashboard.
                </h1>
                <p className="mt-5 max-w-3xl text-lg leading-8 text-slate-300">
                  {typedText}
                </p>
              </div>

              <div className="flex items-center gap-3">
                <button
                  type="button"
                  onClick={() => setDarkMode((value) => !value)}
                  className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-3 text-sm font-semibold text-slate-100 transition hover:border-cyan-300/40 hover:bg-cyan-300/10"
                >
                  {darkMode ? <FiSun /> : <FiMoon />} {darkMode ? 'Light' : 'Dark'} Mode
                </button>
                <div className="rounded-full border border-white/10 bg-white/5 px-4 py-3 text-sm font-semibold text-slate-100">
                  {health}
                </div>
              </div>
            </div>

            <div className="mt-6 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
              {stats.map((stat) => (
                <div key={stat.label} className="rounded-2xl border border-white/10 bg-white/5 p-4">
                  <p className="text-xs uppercase tracking-[0.3em] text-slate-400">{stat.label}</p>
                  <p className="mt-2 text-xl font-semibold text-white">{stat.value}</p>
                </div>
              ))}
            </div>
          </motion.section>

          <div className="grid gap-6 2xl:grid-cols-[1.1fr_0.9fr]">
            <UploadPanel
              preview={preview}
              fileName={file?.name || ''}
              loading={loading}
              modelReady={modelReady}
              onFileSelect={handleFileSelect}
              onPredict={() => runPrediction(undefined, 'Uploaded image')}
              onClear={clearUpload}
              error={error}
            />

            <PredictionCard
              ref={predictionCardRef}
              result={result}
              loading={loading}
              onDownloadImage={downloadPredictionImage}
              onDownloadPdf={downloadPredictionPdf}
            />
          </div>

          <div className="grid gap-6 2xl:grid-cols-[1fr_1fr]">
            <DrawingCanvas loading={loading} modelReady={modelReady} onPredict={runPrediction} />
            <HistoryPanel history={history} onClearHistory={clearHistory} />
          </div>

          <MetricsSection metrics={metrics} assetUrls={assetUrls} />
        </main>
      </div>

      <div className="fixed bottom-6 right-6 z-20 hidden rounded-full border border-white/10 bg-white/8 px-4 py-3 text-xs font-semibold uppercase tracking-[0.3em] text-cyan-100 shadow-glow backdrop-blur-xl lg:block">
        <FiZap className="inline-block" /> Neural UI Active
      </div>
    </div>
  );
}