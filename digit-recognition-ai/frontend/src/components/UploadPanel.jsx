import React, { useRef, useState } from 'react';
import { motion } from 'framer-motion';
import { FiCloud, FiUpload, FiX } from 'react-icons/fi';

const MAX_SIZE_MB = 10;

export default function UploadPanel({ preview, fileName, loading, modelReady, onFileSelect, onPredict, onClear, error }) {
  const inputRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);

  const validateAndSend = (file) => {
    if (!file) return;
    if (!file.type.startsWith('image/')) {
      onClear('Please upload a JPG, PNG, or BMP image.');
      return;
    }
    if (file.size > MAX_SIZE_MB * 1024 * 1024) {
      onClear(`File size must be below ${MAX_SIZE_MB}MB.`);
      return;
    }
    onFileSelect(file);
  };

  const handleDrop = (event) => {
    event.preventDefault();
    setIsDragging(false);
    validateAndSend(event.dataTransfer.files?.[0]);
  };

  return (
    <motion.section
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.55 }}
      className="glass-card rounded-[30px] p-6 shadow-glow"
    >
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.35em] text-cyan-200/70">Upload Studio</p>
          <h3 className="mt-2 text-2xl font-semibold text-white">Drag and drop a handwritten digit</h3>
        </div>
        <button
          type="button"
          onClick={() => inputRef.current?.click()}
          className="neon-button inline-flex items-center gap-2 rounded-full px-5 py-3 text-sm font-semibold"
        >
          <FiUpload /> Browse
        </button>
      </div>

      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        className="hidden"
        onChange={(event) => validateAndSend(event.target.files?.[0])}
      />

      <div
        onDragOver={(event) => {
          event.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        className={`mt-6 cursor-pointer rounded-[28px] border border-dashed transition-all duration-300 ${
          isDragging ? 'border-cyan-300 bg-cyan-300/10' : 'border-white/15 bg-white/5 hover:border-cyan-300/60 hover:bg-white/8'
        }`}
      >
        <div className="flex flex-col items-center justify-center gap-4 px-6 py-12 text-center">
          {preview ? (
            <img src={preview} alt="Uploaded digit preview" className="h-56 w-full max-w-[320px] rounded-3xl object-contain shadow-2xl" />
          ) : (
            <div className="flex flex-col items-center gap-4">
              <div className="flex h-20 w-20 items-center justify-center rounded-3xl bg-cyan-400/15 text-4xl text-cyan-200 shadow-[0_0_30px_rgba(34,211,238,0.25)]">
                <FiCloud />
              </div>
              <div>
                <p className="text-lg font-semibold text-white">Drop your JPG image here</p>
                <p className="mt-2 text-sm text-slate-400">
                  JPG, PNG, or BMP • max {MAX_SIZE_MB}MB • images should contain a single handwritten digit
                </p>
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="mt-5 flex flex-wrap items-center gap-3">
        <button
          type="button"
          onClick={onPredict}
          disabled={!preview || loading || !modelReady}
          className="neon-button inline-flex items-center gap-2 rounded-full px-5 py-3 text-sm font-semibold disabled:cursor-not-allowed disabled:opacity-40"
        >
          <FiUpload /> {loading ? 'Predicting...' : modelReady ? 'Predict Digit' : 'Model Not Trained'}
        </button>
        <button
          type="button"
          onClick={onClear}
          className="inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/5 px-5 py-3 text-sm font-semibold text-slate-200 transition hover:border-white/30 hover:bg-white/10"
        >
          <FiX /> Reset
        </button>
        {fileName ? <span className="text-sm text-slate-400">{fileName}</span> : null}
      </div>

      {!modelReady ? (
        <div className="mt-4 rounded-2xl border border-amber-300/20 bg-amber-400/10 px-4 py-3 text-sm text-amber-100">
          The backend model is not trained yet, so predictions are disabled. Place the digit folders in the dataset and run <span className="font-semibold">python train_model.py</span> inside the backend folder.
        </div>
      ) : null}

      {error ? <p className="mt-4 rounded-2xl border border-rose-400/25 bg-rose-500/10 px-4 py-3 text-sm text-rose-100">{error}</p> : null}
    </motion.section>
  );
}