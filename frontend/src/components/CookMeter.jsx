import { useEffect, useMemo, useRef, useState } from "react";
import { motion, useMotionValue, animate } from "framer-motion";
import { faceForScore, severityForScore } from "../utils/score.js";

const SIZE = 260;
const STROKE = 18;
const RADIUS = (SIZE - STROKE) / 2;
const CIRC = 2 * Math.PI * RADIUS;

function colorStopsForScore(score) {
  if (score >= 86) return ["#ff3b30", "#7f0f0a"];
  if (score >= 71) return ["#ff5c16", "#7a1f00"];
  if (score >= 51) return ["#ffa874", "#c72b0c"];
  if (score >= 31) return ["#ffd166", "#ff803c"];
  if (score >= 11) return ["#86efac", "#22c55e"];
  return ["#22c55e", "#065f46"];
}

export default function CookMeter({ score = 0, size = SIZE, showFace = true }) {
  const severity = useMemo(() => severityForScore(score), [score]);
  const face = faceForScore(score);
  const [displayed, setDisplayed] = useState(0);
  const mv = useMotionValue(0);
  const lastScore = useRef(score);

  // Animate the numeric counter whenever the score changes
  useEffect(() => {
    const controls = animate(mv, score, {
      duration: 1.1,
      ease: "easeOut",
      onUpdate: (v) => setDisplayed(v),
    });
    return () => controls.stop();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [score]);

  // Track last score for potential future delta indicators
  useEffect(() => {
    lastScore.current = score;
  }, [score]);

  const [c1, c2] = colorStopsForScore(score);
  const gradientId = useMemo(
    () => `cookmeter-grad-${Math.random().toString(36).slice(2, 8)}`,
    []
  );

  const progress = Math.max(0, Math.min(1, displayed / 100));
  const dashOffset = CIRC * (1 - progress);

  return (
    <div className="relative mx-auto" style={{ width: size, height: size }}>
      <svg
        width={size}
        height={size}
        viewBox={`0 0 ${size} ${size}`}
        className="-rotate-90"
        aria-hidden="true"
      >
        <defs>
          <linearGradient id={gradientId} x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor={c1} />
            <stop offset="100%" stopColor={c2} />
          </linearGradient>
        </defs>

        {/* Track */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={RADIUS}
          stroke="rgba(255,255,255,0.08)"
          strokeWidth={STROKE}
          fill="none"
        />

        {/* Progress */}
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={RADIUS}
          stroke={`url(#${gradientId})`}
          strokeWidth={STROKE}
          strokeLinecap="round"
          fill="none"
          strokeDasharray={CIRC}
          animate={{ strokeDashoffset: dashOffset }}
          transition={{ duration: 0.25, ease: "linear" }}
          style={{ filter: `drop-shadow(0 0 10px ${c1}55)` }}
        />
      </svg>

      {/* Center content */}
      <div className="absolute inset-0 grid place-items-center">
        <div className="text-center">
          {showFace && (
            <div className="mb-1 text-3xl sm:text-4xl">{face}</div>
          )}
          <div className="font-display text-5xl font-extrabold tabular-nums sm:text-6xl">
            {Math.round(displayed)}%
          </div>
          <div className={`mt-1 text-xs font-semibold uppercase tracking-wider ${severity.tone}`}>
            {severity.pretty}
          </div>
        </div>
      </div>
    </div>
  );
}