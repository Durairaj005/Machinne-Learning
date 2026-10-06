import React, { forwardRef } from 'react';
import { motion } from 'framer-motion';
import { FiArrowUpRight, FiCheckCircle, FiDownload } from 'react-icons/fi';

function confidenceGradient(confidence) {
  return `conic-gradient(#22d3ee ${confidence}%, rgba(255,255,255,0.08) 0)`;
}

const PredictionCard = forwardRef(function PredictionCard(
  { result, loading, onDownloadImage, onDownloadPdf },
  ref,
) {
  const confidence = result?.confidence ?? 0;
  const predictedDigit = result?.predicted_digit ?? null;

  return (
    <div
      ref={ref}
      className="glass-card flex flex-col justify-between rounded-3xl p-5 shadow-glow"
    >
      {/* Header */}
      <div className="flex items-center justify-between border-b border-white/10 pb-4">
        <div>
          <h3 className="text-base font-bold text-white">Live AI Prediction</h3>
          <p className="text-[11px] text-slate-400">TensorFlow CNN Inference</p>
        </div>
        {result && (
          <span className="inline-flex items-center gap-1 rounded-full border border-emerald-400/20 bg-emerald-400/10 px-2.5 py-1 text-[11px] font-medium text-emerald-300">
            <FiCheckCircle className="text-xs" /> Analyzed
          </span>
        )}
      </div>

      {/* Main Content */}
      <div className="py-4">
        {loading ? (
          <div className="flex flex-col items-center justify-center py-12">
            <div className="h-28 w-28 animate-spin rounded-full border-4 border-white/10 border-t-cyan-400" />
            <p className="mt-4 text-xs font-semibold uppercase tracking-wider text-cyan-300">
              Neural network processing...
            </p>
          </div>
        ) : result ? (
          <div className="grid gap-5 md:grid-cols-[160px_1fr] items-center">
            {/* Primary Gauge */}
            <div className="flex flex-col items-center justify-center rounded-2xl border border-white/10 bg-white/5 p-4 text-center">
              <div className="relative flex h-32 w-32 items-center justify-center">
                <div
                  className="absolute inset-0 rounded-full transition-all duration-700"
                  style={{ background: confidenceGradient(confidence) }}
                />
                <div className="absolute inset-2.5 rounded-full border border-white/10 bg-[#020817]" />
                <div className="relative z-10 text-center">
                  <span className="text-5xl font-black text-white">{predictedDigit}</span>
                  <p className="text-[10px] uppercase tracking-wider text-cyan-300">Digit</p>
                </div>
              </div>
              <div className="mt-2 text-center">
                <span className="text-lg font-bold text-cyan-300">{confidence.toFixed(1)}%</span>
                <p className="text-[10px] text-slate-400">Confidence</p>
              </div>
            </div>

            {/* Probability Breakdown */}
            <div className="space-y-3">
              {/* Top 3 Badges */}
              <div className="grid grid-cols-3 gap-2">
                {result.top_predictions?.map((item, idx) => (
                  <div
                    key={item.digit}
                    className={`rounded-xl border p-2 text-center transition ${
                      idx === 0
                        ? 'border-cyan-400/40 bg-cyan-400/10'
                        : 'border-white/10 bg-white/5'
                    }`}
                  >
                    <span className="text-[10px] text-slate-400">
                      {idx === 0 ? '🏆 1st' : idx === 1 ? '2nd' : '3rd'}
                    </span>
                    <p className="text-base font-bold text-white">{item.digit}</p>
                    <p className="text-[10px] font-medium text-cyan-300">{item.probability}%</p>
                  </div>
                ))}
              </div>

              {/* 0-9 Micro Bar Chart */}
              <div className="grid grid-cols-2 gap-1.5 pt-1">
                {(result.probabilities || []).map((prob, digit) => {
                  const isWinner = digit === predictedDigit;
                  return (
                    <div
                      key={digit}
                      className={`flex items-center gap-2 rounded-lg px-2 py-1 text-xs transition ${
                        isWinner
                          ? 'border border-cyan-400/30 bg-cyan-400/15'
                          : 'bg-white/5'
                      }`}
                    >
                      <span className={`w-3 font-bold ${isWinner ? 'text-cyan-300' : 'text-slate-300'}`}>
                        {digit}
                      </span>
                      <div className="h-2 flex-1 overflow-hidden rounded-full bg-white/10">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${Math.min(100, prob * 100)}%` }}
                          transition={{ duration: 0.5, ease: 'easeOut' }}
                          className={`h-full rounded-full ${
                            isWinner
                              ? 'bg-gradient-to-r from-cyan-400 to-sky-400'
                              : 'bg-slate-400'
                          }`}
                        />
                      </div>
                      <span className="w-9 text-right text-[10px] text-slate-400">
                        {(prob * 100).toFixed(0)}%
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-white/10 py-16 text-center text-slate-400">
            <p className="text-sm font-medium text-slate-300">Awaiting digit input</p>
            <p className="mt-1 text-xs text-slate-500">
              Draw a digit on the canvas or upload an image to see live prediction
            </p>
          </div>
        )}
      </div>

      {/* Footer Export Controls */}
      <div className="flex items-center justify-between border-t border-white/10 pt-3">
        <span className="text-[11px] text-slate-400">Export card:</span>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={onDownloadImage}
            disabled={!result}
            className="inline-flex items-center gap-1.5 rounded-lg border border-white/10 bg-white/5 px-3 py-1.5 text-xs font-semibold text-slate-200 transition hover:bg-white/10 disabled:opacity-40"
          >
            <FiDownload /> PNG
          </button>
          <button
            type="button"
            onClick={onDownloadPdf}
            disabled={!result}
            className="inline-flex items-center gap-1.5 rounded-lg border border-white/10 bg-white/5 px-3 py-1.5 text-xs font-semibold text-slate-200 transition hover:bg-white/10 disabled:opacity-40"
          >
            <FiDownload /> PDF
          </button>
        </div>
      </div>
    </div>
  );
});

export default PredictionCard;