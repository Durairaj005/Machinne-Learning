import React, { forwardRef } from 'react';
import { motion } from 'framer-motion';
import { FiArrowUpRight } from 'react-icons/fi';

function confidenceGradient(confidence) {
  return `conic-gradient(#22d3ee ${confidence}%, rgba(255,255,255,0.08) 0)`;
}

const PredictionCard = forwardRef(function PredictionCard(
  { result, loading, onDownloadImage, onDownloadPdf },
  ref,
) {
  const confidence = result?.confidence ?? 0;

  return (
    <motion.section
      ref={ref}
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.55 }}
      className="glass-card rounded-[30px] p-6 shadow-glow"
    >
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.35em] text-cyan-200/70">AI Prediction Dashboard</p>
          <h3 className="mt-2 text-2xl font-semibold text-white">Prediction Reveal</h3>
        </div>
        {result ? (
          <div className="rounded-full border border-emerald-400/20 bg-emerald-400/10 px-4 py-2 text-sm font-medium text-emerald-100">
            Processed successfully
          </div>
        ) : null}
      </div>

      {loading ? (
        <div className="mt-6 rounded-[28px] border border-white/10 bg-white/5 p-8">
          <div className="h-8 w-40 animate-pulse rounded-full bg-white/10" />
          <div className="mt-6 flex items-center gap-6">
            <div className="h-36 w-36 animate-pulse rounded-full bg-white/10" />
            <div className="flex-1 space-y-4">
              <div className="h-4 w-3/4 animate-pulse rounded-full bg-white/10" />
              <div className="h-4 w-1/2 animate-pulse rounded-full bg-white/10" />
              <div className="h-4 w-2/3 animate-pulse rounded-full bg-white/10" />
            </div>
          </div>
        </div>
      ) : result ? (
        <div className="mt-6 grid gap-6 xl:grid-cols-[240px_1fr]">
          <div className="flex flex-col items-center justify-center rounded-[28px] border border-cyan-300/15 bg-white/5 p-6 text-center">
            <div className="relative flex h-44 w-44 items-center justify-center">
              <div className="absolute inset-0 rounded-full" style={{ background: confidenceGradient(confidence) }} />
              <div className="absolute inset-3 rounded-full border border-white/10 bg-[#020817]" />
              <div className="relative z-10 text-center">
                <p className="text-5xl font-black text-white">{result.predicted_digit}</p>
                <p className="mt-2 text-xs uppercase tracking-[0.3em] text-cyan-200/75">Predicted Digit</p>
              </div>
            </div>
            <p className="mt-5 text-sm text-slate-400">Confidence</p>
            <p className="mt-1 text-3xl font-semibold text-cyan-200">{confidence.toFixed(2)}%</p>
          </div>

          <div className="space-y-6">
            <div className="grid gap-4 md:grid-cols-3">
              {result.top_predictions?.map((item) => (
                <div key={item.digit} className="rounded-2xl border border-white/10 bg-white/5 p-4">
                  <p className="text-xs uppercase tracking-[0.25em] text-slate-400">Top Guess</p>
                  <p className="mt-2 text-3xl font-bold text-white">{item.digit}</p>
                  <p className="mt-1 text-sm text-cyan-200">{item.probability}%</p>
                </div>
              ))}
            </div>

            <div className="grid gap-3">
              {(result.probabilities || []).map((probability, index) => (
                <div key={index} className="grid grid-cols-[40px_1fr_72px] items-center gap-3 rounded-2xl border border-white/10 bg-white/5 px-4 py-3">
                  <span className="text-sm font-semibold text-white">{index}</span>
                  <div className="h-3 overflow-hidden rounded-full bg-white/10">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${probability * 100}%` }}
                      transition={{ duration: 0.8, ease: 'easeOut' }}
                      className="h-full rounded-full bg-gradient-to-r from-cyan-400 via-sky-400 to-fuchsia-500"
                    />
                  </div>
                  <span className="text-right text-sm text-slate-300">{(probability * 100).toFixed(1)}%</span>
                </div>
              ))}
            </div>

            <div className="flex flex-wrap gap-3">
              <button
                type="button"
                onClick={onDownloadImage}
                className="inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/5 px-4 py-2 text-sm font-semibold text-slate-100 transition hover:border-cyan-300/50 hover:bg-cyan-300/10"
              >
                <FiArrowUpRight /> Download PNG
              </button>
              <button
                type="button"
                onClick={onDownloadPdf}
                className="inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/5 px-4 py-2 text-sm font-semibold text-slate-100 transition hover:border-cyan-300/50 hover:bg-cyan-300/10"
              >
                <FiArrowUpRight /> Download PDF
              </button>
            </div>
          </div>
        </div>
      ) : (
        <div className="mt-6 rounded-[28px] border border-dashed border-white/10 bg-white/5 p-8 text-center text-slate-400">
          Upload an image or draw a digit to reveal the model prediction here.
        </div>
      )}
    </motion.section>
  );
});

export default PredictionCard;