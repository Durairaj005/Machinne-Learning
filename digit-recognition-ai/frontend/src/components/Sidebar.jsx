import React from 'react';
import { motion } from 'framer-motion';
import { FiActivity, FiCpu, FiDatabase, FiLayers, FiZap } from 'react-icons/fi';

const items = [
  { icon: FiCpu, label: 'TensorFlow CNN' },
  { icon: FiLayers, label: 'React + Tailwind' },
  { icon: FiZap, label: 'Framer Motion UI' },
  { icon: FiDatabase, label: 'MNIST JPG Dataset' },
];

export default function Sidebar({ modelReady, apiStatus }) {
  return (
    <motion.aside
      initial={{ opacity: 0, x: -24 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.6 }}
      className="glass-card sticky top-6 flex h-fit flex-col gap-6 rounded-[28px] p-6 shadow-glow"
    >
      <div>
        <p className="text-xs uppercase tracking-[0.35em] text-cyan-200/80">Project Control Panel</p>
        <h2 className="mt-3 text-2xl font-semibold text-white">AI Digit Recognition</h2>
        <p className="mt-3 text-sm leading-6 text-slate-300">
          Predict handwritten digits from uploaded JPG images or from the drawing canvas using a trained CNN backend.
        </p>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
          <p className="text-xs text-slate-400">Model</p>
          <p className="mt-1 text-lg font-semibold text-white">{modelReady ? 'Ready' : 'Not trained'}</p>
        </div>
        <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
          <p className="text-xs text-slate-400">API</p>
          <p className="mt-1 text-lg font-semibold text-white">{apiStatus}</p>
        </div>
      </div>

      <div className="space-y-3">
        {items.map(({ icon: Icon, label }) => (
          <div key={label} className="flex items-center gap-3 rounded-2xl border border-white/10 bg-white/5 px-4 py-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-cyan-400/15 text-cyan-200">
              <Icon />
            </div>
            <span className="text-sm font-medium text-slate-200">{label}</span>
          </div>
        ))}
      </div>

      <div className="rounded-2xl border border-cyan-400/20 bg-cyan-400/10 p-4">
        <div className="flex items-center gap-2 text-cyan-100">
          <FiActivity />
          <span className="text-sm font-semibold uppercase tracking-[0.2em]">Local Demo Ready</span>
        </div>
        <p className="mt-2 text-sm leading-6 text-slate-300">
          This interface is set up as a local presentation website for demos in VS Code with the API running on your machine.
        </p>
      </div>
    </motion.aside>
  );
}