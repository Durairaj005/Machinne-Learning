import React from 'react';
import { motion } from 'framer-motion';
import { FiClock, FiTrash2 } from 'react-icons/fi';

export default function HistoryPanel({ history, onClearHistory }) {
  return (
    <motion.section
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.55 }}
      className="glass-card rounded-[30px] p-6 shadow-glow"
    >
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.35em] text-cyan-200/70">Prediction History</p>
          <h3 className="mt-2 text-2xl font-semibold text-white">Recent Outputs</h3>
        </div>
        <button
          type="button"
          onClick={onClearHistory}
          className="inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/5 px-4 py-2 text-sm font-semibold text-slate-200 transition hover:border-rose-400/50 hover:bg-rose-500/10"
        >
          <FiTrash2 /> Clear History
        </button>
      </div>

      <div className="mt-6 space-y-3">
        {history.length ? (
          history.map((entry) => (
            <div key={entry.id} className="flex flex-wrap items-center justify-between gap-4 rounded-2xl border border-white/10 bg-white/5 px-4 py-3">
              <div>
                <p className="text-sm font-semibold text-white">Digit {entry.digit}</p>
                <p className="mt-1 text-xs text-slate-400">{entry.source} • {entry.time}</p>
              </div>
              <div className="flex items-center gap-2 text-sm text-cyan-200">
                <FiClock /> {entry.confidence}% confidence
              </div>
            </div>
          ))
        ) : (
          <div className="rounded-2xl border border-dashed border-white/10 bg-white/5 p-6 text-sm text-slate-400">
            Predictions will appear here after you upload an image or use the canvas.
          </div>
        )}
      </div>
    </motion.section>
  );
}