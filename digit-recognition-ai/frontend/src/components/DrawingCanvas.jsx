import React, { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';
import { FiEdit3, FiPlay, FiRotateCcw } from 'react-icons/fi';

export default function DrawingCanvas({ onPredict, loading, modelReady }) {
  const canvasRef = useRef(null);
  const drawing = useRef(false);
  const [livePredict, setLivePredict] = useState(true);

  const resizeCanvas = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const context = canvas.getContext('2d');
    canvas.width = 280;
    canvas.height = 280;
    context.fillStyle = '#ffffff';
    context.fillRect(0, 0, canvas.width, canvas.height);
    context.lineCap = 'round';
    context.lineJoin = 'round';
    context.strokeStyle = '#111827';
    context.lineWidth = 22;
  };

  useEffect(() => {
    resizeCanvas();
  }, []);

  const getPosition = (event) => {
    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const clientX = event.touches?.[0]?.clientX ?? event.clientX;
    const clientY = event.touches?.[0]?.clientY ?? event.clientY;
    return {
      x: ((clientX - rect.left) / rect.width) * canvas.width,
      y: ((clientY - rect.top) / rect.height) * canvas.height,
    };
  };

  const startDrawing = (event) => {
    drawing.current = true;
    draw(event);
  };

  const draw = (event) => {
    if (!drawing.current) return;
    event.preventDefault();
    const canvas = canvasRef.current;
    const context = canvas.getContext('2d');
    const { x, y } = getPosition(event);
    context.lineTo(x, y);
    context.stroke();
    context.beginPath();
    context.moveTo(x, y);
  };

  const endDrawing = async () => {
    if (!drawing.current) return;
    drawing.current = false;
    canvasRef.current.getContext('2d').beginPath();
    if (livePredict) {
      await predictNow();
    }
  };

  const clearCanvas = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const context = canvas.getContext('2d');
    context.clearRect(0, 0, canvas.width, canvas.height);
    context.fillStyle = '#ffffff';
    context.fillRect(0, 0, canvas.width, canvas.height);
  };

  const predictNow = async () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    if (!modelReady) return;
    const dataUrl = canvas.toDataURL('image/png');
    await onPredict(dataUrl, 'Canvas drawing');
  };

  return (
    <motion.section
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.55 }}
      className="glass-card rounded-[30px] p-6 shadow-glow"
    >
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.35em] text-cyan-200/70">Digit Canvas</p>
          <h3 className="mt-2 text-2xl font-semibold text-white">Draw a digit directly</h3>
        </div>
        <label className="flex items-center gap-3 rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-slate-200">
          <input type="checkbox" checked={livePredict} onChange={(event) => setLivePredict(event.target.checked)} />
          Live predict
        </label>
      </div>

      <div className="mt-6 flex justify-center">
        <div className="rounded-[28px] border border-white/10 bg-gradient-to-br from-white/10 to-cyan-400/5 p-4 shadow-2xl">
          <canvas
            ref={canvasRef}
            width={280}
            height={280}
            className="touch-none rounded-[22px] bg-white shadow-inner"
            onPointerDown={startDrawing}
            onPointerMove={draw}
            onPointerUp={endDrawing}
            onPointerLeave={endDrawing}
            onTouchStart={startDrawing}
            onTouchMove={draw}
            onTouchEnd={endDrawing}
          />
        </div>
      </div>

      <div className="mt-5 flex flex-wrap items-center gap-3">
        <button
          type="button"
          onClick={clearCanvas}
          className="inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/5 px-4 py-2 text-sm font-semibold text-slate-100 transition hover:border-white/30 hover:bg-white/10"
        >
          <FiRotateCcw /> Clear Canvas
        </button>
        <button
          type="button"
          onClick={predictNow}
          disabled={loading || !modelReady}
          className="neon-button inline-flex items-center gap-2 rounded-full px-5 py-2.5 text-sm font-semibold disabled:cursor-not-allowed disabled:opacity-40"
        >
          <FiPlay /> {loading ? 'Predicting...' : modelReady ? 'Predict Drawing' : 'Model Not Trained'}
        </button>
        <span className="inline-flex items-center gap-2 text-sm text-slate-400">
          <FiEdit3 /> Use thick strokes centered in the canvas for best results.
        </span>
      </div>

      {!modelReady ? (
        <p className="mt-4 rounded-2xl border border-amber-300/20 bg-amber-400/10 px-4 py-3 text-sm text-amber-100">
          Canvas prediction is waiting for a trained model. Run the training script first, then refresh the page.
        </p>
      ) : null}
    </motion.section>
  );
}