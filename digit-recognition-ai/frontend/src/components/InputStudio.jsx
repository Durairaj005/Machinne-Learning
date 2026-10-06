import React, { useRef, useState } from 'react';
import { motion } from 'framer-motion';
import { FiCloud, FiEdit3, FiImage, FiUpload, FiX } from 'react-icons/fi';
import DrawingCanvas from './DrawingCanvas';

const MAX_SIZE_MB = 10;

export default function InputStudio({
  preview,
  fileName,
  loading,
  modelReady,
  onFileSelect,
  onPredictUpload,
  onPredictCanvas,
  onClearUpload,
  error,
}) {
  const [activeTab, setActiveTab] = useState('canvas'); // 'canvas' or 'upload'
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

  const handleFile = (file) => {
    if (!file) return;
    if (!file.type.startsWith('image/')) {
      onClearUpload('Please select a JPG, PNG, or BMP image.');
      return;
    }
    if (file.size > MAX_SIZE_MB * 1024 * 1024) {
      onClearUpload(`File must be smaller than ${MAX_SIZE_MB}MB.`);
      return;
    }
    onFileSelect(file);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    handleFile(e.dataTransfer.files?.[0]);
  };

  return (
    <div className="glass-card flex flex-col rounded-3xl p-5 shadow-glow">
      {/* Tab Switcher */}
      <div className="flex items-center justify-between border-b border-white/10 pb-4">
        <div className="flex items-center gap-1 rounded-xl bg-white/5 p-1">
          <button
            type="button"
            onClick={() => setActiveTab('canvas')}
            className={`inline-flex items-center gap-2 rounded-lg px-4 py-1.5 text-xs font-semibold transition ${
              activeTab === 'canvas'
                ? 'bg-gradient-to-r from-cyan-400 to-sky-500 text-slate-950 shadow-md'
                : 'text-slate-300 hover:text-white'
            }`}
          >
            <FiEdit3 className="text-sm" /> Draw Digit
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('upload')}
            className={`inline-flex items-center gap-2 rounded-lg px-4 py-1.5 text-xs font-semibold transition ${
              activeTab === 'upload'
                ? 'bg-gradient-to-r from-cyan-400 to-sky-500 text-slate-950 shadow-md'
                : 'text-slate-300 hover:text-white'
            }`}
          >
            <FiUpload className="text-sm" /> Upload Image
          </button>
        </div>

        <span className="text-[11px] font-medium text-slate-400">
          {activeTab === 'canvas' ? 'Draw freehand on canvas' : 'Drop handwritten digit image'}
        </span>
      </div>

      {/* Tab Contents */}
      <div className="pt-4">
        {activeTab === 'canvas' ? (
          <DrawingCanvas
            onPredict={onPredictCanvas}
            loading={loading}
            modelReady={modelReady}
          />
        ) : (
          <div className="flex flex-col items-center">
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              className="hidden"
              onChange={(e) => handleFile(e.target.files?.[0])}
            />

            <div
              onDragOver={(e) => {
                e.preventDefault();
                setIsDragging(true);
              }}
              onDragLeave={() => setIsDragging(false)}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className={`flex h-[280px] w-full max-w-[340px] cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed p-4 text-center transition ${
                isDragging
                  ? 'border-cyan-300 bg-cyan-300/10'
                  : 'border-white/15 bg-white/5 hover:border-cyan-300/50 hover:bg-white/8'
              }`}
            >
              {preview ? (
                <div className="relative flex h-full w-full items-center justify-center">
                  <img
                    src={preview}
                    alt="Digit preview"
                    className="max-h-full max-w-full rounded-xl object-contain shadow-lg"
                  />
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      onClearUpload();
                    }}
                    className="absolute right-1 top-1 rounded-full bg-slate-900/80 p-1.5 text-slate-300 hover:text-white"
                  >
                    <FiX />
                  </button>
                </div>
              ) : (
                <div className="flex flex-col items-center gap-3">
                  <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-cyan-400/15 text-2xl text-cyan-300 shadow-[0_0_20px_rgba(34,211,238,0.2)]">
                    <FiCloud />
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-white">Drop digit image here</p>
                    <p className="mt-1 text-xs text-slate-400">JPG, PNG, BMP up to 10MB</p>
                  </div>
                  <span className="rounded-lg border border-white/10 bg-white/5 px-3 py-1 text-xs font-medium text-slate-300">
                    Click to browse
                  </span>
                </div>
              )}
            </div>

            <div className="mt-4 flex w-full items-center justify-between gap-2">
              <button
                type="button"
                onClick={onClearUpload}
                disabled={!preview}
                className="inline-flex items-center gap-1.5 rounded-xl border border-white/15 bg-white/5 px-4 py-2 text-xs font-semibold text-slate-200 transition hover:border-white/30 hover:bg-white/10 disabled:opacity-40"
              >
                <FiX /> Reset
              </button>

              <button
                type="button"
                onClick={onPredictUpload}
                disabled={!preview || loading || !modelReady}
                className="neon-button inline-flex items-center gap-2 rounded-xl px-5 py-2 text-xs font-semibold disabled:cursor-not-allowed disabled:opacity-40"
              >
                <FiUpload /> {loading ? 'Recognizing...' : 'Predict Image'}
              </button>
            </div>

            {fileName && (
              <p className="mt-2 text-center text-xs text-slate-400">
                Selected: <span className="font-medium text-cyan-300">{fileName}</span>
              </p>
            )}
          </div>
        )}
      </div>

      {error && (
        <p className="mt-3 rounded-xl border border-rose-400/20 bg-rose-500/10 px-3 py-2 text-xs text-rose-200">
          {error}
        </p>
      )}
    </div>
  );
}
