import React from 'react';
import { motion } from 'framer-motion';
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

function MetricCard({ label, value, tone }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
      <p className="text-xs uppercase tracking-[0.3em] text-slate-400">{label}</p>
      <p className={`mt-2 text-3xl font-bold ${tone}`}>{value}</p>
    </div>
  );
}

export default function MetricsSection({ metrics, assetUrls }) {
  const history = metrics?.history || {};
  const chartData = (history.accuracy || []).map((accuracy, index) => ({
    epoch: index + 1,
    accuracy: accuracy * 100,
    validation: (history.val_accuracy?.[index] || 0) * 100,
    loss: history.loss?.[index] ?? 0,
    valLoss: history.val_loss?.[index] ?? 0,
  }));

  const trainAccuracy = history.accuracy?.length ? `${(history.accuracy[history.accuracy.length - 1] * 100).toFixed(2)}%` : 'N/A';
  const valAccuracy = history.val_accuracy?.length ? `${(history.val_accuracy[history.val_accuracy.length - 1] * 100).toFixed(2)}%` : 'N/A';

  return (
    <motion.section
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.55 }}
      className="glass-card rounded-[30px] p-6 shadow-glow"
    >
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.35em] text-cyan-200/70">Model Visualization</p>
          <h3 className="mt-2 text-2xl font-semibold text-white">Training Intelligence</h3>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <MetricCard label="Training Accuracy" value={trainAccuracy} tone="text-cyan-200" />
          <MetricCard label="Validation Accuracy" value={valAccuracy} tone="text-fuchsia-200" />
        </div>
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-[1.6fr_1fr]">
        <div className="rounded-[28px] border border-white/10 bg-white/5 p-4">
          <div className="mb-4 flex items-center justify-between">
            <p className="text-sm font-semibold text-white">Accuracy and loss curve</p>
            <span className="text-xs uppercase tracking-[0.25em] text-slate-400">Animated chart</span>
          </div>
          <div className="h-[340px]">
            {chartData.length ? (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData} margin={{ top: 10, right: 18, left: -10, bottom: 0 }}>
                  <CartesianGrid stroke="rgba(255,255,255,0.08)" strokeDasharray="4 4" />
                  <XAxis dataKey="epoch" stroke="#94a3b8" />
                  <YAxis stroke="#94a3b8" />
                  <Tooltip
                    contentStyle={{
                      background: '#0f172a',
                      border: '1px solid rgba(255,255,255,0.12)',
                      borderRadius: '16px',
                    }}
                  />
                  <Line type="monotone" dataKey="accuracy" stroke="#22d3ee" strokeWidth={3} dot={false} />
                  <Line type="monotone" dataKey="validation" stroke="#a855f7" strokeWidth={3} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex h-full items-center justify-center text-slate-400">
                Train the model to render accuracy charts here.
              </div>
            )}
          </div>
        </div>

        <div className="space-y-4">
          <div className="rounded-[28px] border border-white/10 bg-white/5 p-4">
            <p className="text-sm font-semibold text-white">Model artifacts</p>
            <div className="mt-4 space-y-4">
              {assetUrls.training_curves ? (
                <img src={assetUrls.training_curves} alt="Training curves" className="w-full rounded-2xl border border-white/10" />
              ) : null}
              {assetUrls.confusion_matrix ? (
                <img src={assetUrls.confusion_matrix} alt="Confusion matrix" className="w-full rounded-2xl border border-white/10" />
              ) : null}
            </div>
          </div>

          <div className="rounded-[28px] border border-white/10 bg-white/5 p-4">
            <p className="text-sm font-semibold text-white">Sample predictions</p>
            <div className="mt-4 overflow-hidden rounded-2xl border border-white/10">
              {assetUrls.sample_predictions ? (
                <img src={assetUrls.sample_predictions} alt="Sample predictions" className="w-full" />
              ) : (
                <div className="p-6 text-sm text-slate-400">Generate sample prediction visuals during training.</div>
              )}
            </div>
          </div>
        </div>
      </div>
    </motion.section>
  );
}