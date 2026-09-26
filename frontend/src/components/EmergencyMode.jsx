import { motion } from "framer-motion";
import { AlertTriangle, RefreshCw } from "lucide-react";

const STEPS = [
  { n: 1, t: "Stop everything unrelated.", d: "Close the tabs. Mute the group chat." },
  { n: 2, t: "Identify the single most important task.", d: "Not the second. Not the third. The first." },
  { n: 3, t: "Set a 25-minute timer.", d: "Phone in another room. Timer visible." },
  { n: 4, t: "Work without distractions.", d: "No notes apps. No 'quick check'. Just work." },
  { n: 5, t: "Recalculate your situation.", d: "Come back and reassess once the timer rings." },
];

export default function EmergencyMode({ onReassess }) {
  return (
    <motion.section
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="relative overflow-hidden rounded-3xl border border-red-500/40 bg-gradient-to-br from-red-950/60 via-charcoal-900 to-charcoal-950 p-6 sm:p-8"
      role="region"
      aria-label="Emergency mode"
    >
      {/* pulse glow */}
      <motion.div
        aria-hidden="true"
        className="pointer-events-none absolute -top-24 left-1/2 h-64 w-64 -translate-x-1/2 rounded-full bg-red-500/20 blur-3xl"
        animate={{ opacity: [0.4, 0.85, 0.4] }}
        transition={{ repeat: Infinity, duration: 2.2, ease: "easeInOut" }}
      />

      <div className="relative">
        <div className="mb-1 flex items-center gap-2 text-red-300">
          <AlertTriangle size={18} />
          <span className="text-xs font-semibold uppercase tracking-widest">
            Emergency Mode Activated
          </span>
        </div>
        <h3 className="font-display text-2xl font-extrabold sm:text-3xl">
          🚨 Crisis-recovery plan
        </h3>
        <p className="mt-1 text-sm text-white/60">
          Do these in order. Do not skip. Do not negotiate with yourself.
        </p>

        <ol className="mt-6 grid gap-3 sm:grid-cols-2">
          {STEPS.map((s) => (
            <li
              key={s.n}
              className="flex items-start gap-3 rounded-2xl border border-white/10 bg-white/[0.04] p-4"
            >
              <span className="grid h-8 w-8 shrink-0 place-items-center rounded-xl bg-red-500/20 text-sm font-bold text-red-200">
                {s.n}
              </span>
              <div>
                <div className="font-semibold">{s.t}</div>
                <div className="text-xs text-white/55">{s.d}</div>
              </div>
            </li>
          ))}
        </ol>

        <div className="mt-6 flex flex-wrap items-center gap-3">
          <button onClick={onReassess} className="btn-primary">
            <RefreshCw size={16} /> Reassess me
          </button>
          <span className="text-xs text-white/50">
            Come back after 25 minutes. See if the number drops.
          </span>
        </div>
      </div>
    </motion.section>
  );
}