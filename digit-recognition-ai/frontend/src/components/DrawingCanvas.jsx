import React, { useEffect, useRef, useState } from 'react';
import { FiEdit3, FiPlay, FiRotateCcw, FiZap } from 'react-icons/fi';

export default function DrawingCanvas({ onPredict, loading, modelReady }) {
  const canvasRef = useRef(null);
  const drawing = useRef(false);
  const [brushSize, setBrushSize] = useState(24);
  const [livePredict, setLivePredict] = useState(true);

  const initCanvas = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    canvas.width = 280;
    canvas.height = 280;
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    ctx.strokeStyle = '#000000';
    ctx.lineWidth = brushSize;
  };

  useEffect(() => {
    initCanvas();
  }, []);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    ctx.lineWidth = brushSize;
  }, [brushSize]);

  const getPos = (event) => {
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
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const { x, y } = getPos(event);
    ctx.beginPath();
    ctx.moveTo(x, y);
    ctx.lineTo(x, y);
    ctx.stroke();
  };

  const draw = (event) => {
    if (!drawing.current) return;
    event.preventDefault();
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const { x, y } = getPos(event);
    ctx.lineTo(x, y);
    ctx.stroke();
  };

  const endDrawing = async () => {
    if (!drawing.current) return;
    drawing.current = false;
    const canvas = canvasRef.current;
    if (!canvas) return;
    canvas.getContext('2d').beginPath();
    if (livePredict && modelReady) {
      await predictNow();
    }
  };

  const clearCanvas = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.lineWidth = brushSize;
    ctx.strokeStyle = '#000000';
    ctx.beginPath();
  };

  const predictNow = async () => {
    const canvas = canvasRef.current;
    if (!canvas || !modelReady) return;
    const dataUrl = canvas.toDataURL('image/png');
    await onPredict(dataUrl, 'Canvas drawing');
  };

  // Preset sample digits to easily test drawing prediction with 1 click
  const drawSamplePreset = (digit) => {
    clearCanvas();
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    ctx.lineWidth = 24;
    ctx.strokeStyle = '#000000';
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';

    ctx.beginPath();
    if (digit === 2) {
      // Draw smooth digit 2
      ctx.arc(140, 95, 45, Math.PI, 0, false);
      ctx.bezierCurveTo(185, 120, 160, 175, 95, 215);
      ctx.lineTo(195, 215);
      ctx.stroke();
    } else if (digit === 7) {
      // Draw digit 7
      ctx.moveTo(85, 80);
      ctx.lineTo(195, 80);
      ctx.lineTo(125, 225);
      ctx.stroke();
    } else if (digit === 8) {
      // Draw digit 8
      ctx.arc(140, 105, 36, 0, Math.PI * 2);
      ctx.stroke();
      ctx.beginPath();
      ctx.arc(140, 175, 44, 0, Math.PI * 2);
      ctx.stroke();
    } else if (digit === 3) {
      // Draw digit 3
      ctx.arc(140, 105, 36, Math.PI * 1.3, Math.PI * 0.4);
      ctx.stroke();
      ctx.beginPath();
      ctx.arc(140, 175, 44, Math.PI * 1.6, Math.PI * 0.7);
      ctx.stroke();
    } else if (digit === 0) {
      // Draw digit 0
      ctx.ellipse(140, 140, 45, 75, 0, 0, Math.PI * 2);
      ctx.stroke();
    }
    ctx.beginPath();

    setTimeout(() => {
      predictNow();
    }, 50);
  };

  return (
    <div className="flex flex-col items-center">
      {/* Canvas Header Controls */}
      <div className="flex w-full items-center justify-between gap-2 pb-3 text-xs">
        <div className="flex items-center gap-1.5">
          <span className="text-slate-400">Brush:</span>
          <button
            type="button"
            onClick={() => setBrushSize(18)}
            className={`rounded-lg px-2.5 py-1 text-xs font-semibold transition ${
              brushSize === 18 ? 'bg-cyan-400/20 text-cyan-300 border border-cyan-400/40' : 'bg-white/5 text-slate-300 hover:bg-white/10'
            }`}
          >
            Normal
          </button>
          <button
            type="button"
            onClick={() => setBrushSize(26)}
            className={`rounded-lg px-2.5 py-1 text-xs font-semibold transition ${
              brushSize === 26 ? 'bg-cyan-400/20 text-cyan-300 border border-cyan-400/40' : 'bg-white/5 text-slate-300 hover:bg-white/10'
            }`}
          >
            Thick
          </button>
        </div>

        <label className="flex cursor-pointer items-center gap-2 rounded-lg bg-white/5 px-2.5 py-1 text-slate-300 transition hover:bg-white/10">
          <input
            type="checkbox"
            checked={livePredict}
            onChange={(e) => setLivePredict(e.target.checked)}
            className="h-3.5 w-3.5 accent-cyan-400"
          />
          <span className="text-xs">Live predict</span>
        </label>
      </div>

      {/* Canvas Drawing Board */}
      <div className="relative rounded-2xl border-2 border-white/15 bg-white p-1.5 shadow-[0_0_40px_rgba(34,211,238,0.12)]">
        <canvas
          ref={canvasRef}
          width={280}
          height={280}
          className="touch-none cursor-crosshair rounded-xl bg-white shadow-inner"
          onPointerDown={startDrawing}
          onPointerMove={draw}
          onPointerUp={endDrawing}
          onPointerLeave={endDrawing}
          onTouchStart={startDrawing}
          onTouchMove={draw}
          onTouchEnd={endDrawing}
        />
      </div>

      {/* Action Buttons */}
      <div className="mt-4 flex w-full flex-wrap items-center justify-between gap-2">
        <button
          type="button"
          onClick={clearCanvas}
          className="inline-flex items-center gap-1.5 rounded-xl border border-white/15 bg-white/5 px-4 py-2 text-xs font-semibold text-slate-200 transition hover:border-white/30 hover:bg-white/10 active:scale-95"
        >
          <FiRotateCcw className="text-sm" /> Clear
        </button>

        <button
          type="button"
          onClick={predictNow}
          disabled={loading || !modelReady}
          className="neon-button inline-flex items-center gap-2 rounded-xl px-5 py-2 text-xs font-semibold disabled:cursor-not-allowed disabled:opacity-40"
        >
          <FiPlay /> {loading ? 'Recognizing...' : 'Predict Digit'}
        </button>
      </div>

      {/* Preset Fast Testing Digits */}
      <div className="mt-4 flex w-full items-center justify-between gap-1 rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-xs text-slate-400">
        <span className="inline-flex items-center gap-1 text-[11px] font-medium text-slate-300">
          <FiZap className="text-cyan-400" /> Try sample:
        </span>
        <div className="flex items-center gap-1.5">
          {[2, 7, 8, 3, 0].map((d) => (
            <button
              key={d}
              type="button"
              onClick={() => drawSamplePreset(d)}
              className="flex h-6 w-6 items-center justify-center rounded-md bg-white/10 text-xs font-bold text-white transition hover:bg-cyan-400/20 hover:text-cyan-300 active:scale-90"
              title={`Draw sample digit ${d}`}
            >
              {d}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}