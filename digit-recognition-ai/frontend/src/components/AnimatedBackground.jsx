import React from 'react';

const blobs = [
  'left-[-8rem] top-[-8rem] h-72 w-72 bg-cyan-400/25',
  'right-[-6rem] top-20 h-80 w-80 bg-violet-500/20',
  'left-1/3 bottom-[-7rem] h-96 w-96 bg-fuchsia-500/10',
];

export default function AnimatedBackground() {
  return (
    <div className="pointer-events-none absolute inset-0 overflow-hidden">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(14,165,233,0.18),_transparent_30%),radial-gradient(circle_at_bottom_right,_rgba(168,85,247,0.16),_transparent_24%),linear-gradient(180deg,_#020617_0%,_#020617_45%,_#040816_100%)]" />
      <div className="absolute inset-0 bg-radial-grid bg-[length:28px_28px] opacity-[0.12]" />
      {blobs.map((className, index) => (
        <div
          key={className}
          className={`absolute rounded-full blur-3xl ${className} ${index % 2 === 0 ? 'animate-floaty' : 'animate-drift'}`}
        />
      ))}
      <div className="absolute inset-0 bg-[linear-gradient(120deg,transparent,rgba(255,255,255,0.06),transparent)] bg-[length:200%_100%] animate-shine opacity-25" />
    </div>
  );
}