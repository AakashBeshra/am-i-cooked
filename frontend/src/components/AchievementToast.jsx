import { motion } from "framer-motion";

/**
 * Custom toast content for achievement unlocks. Wired up in AppContext
 * via `toast.custom(...)` — see the update to AppContext.jsx below.
 */
export default function AchievementToast({ achievement, t }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: -20, scale: 0.95 }}
      animate={{
        opacity: t.visible ? 1 : 0,
        y: t.visible ? 0 : -20,
        scale: t.visible ? 1 : 0.95,
      }}
      transition={{ duration: 0.25, ease: "easeOut" }}
      className="pointer-events-auto w-[340px] max-w-[90vw] overflow-hidden rounded-2xl border border-ember-500/40 bg-gradient-to-br from-ember-950/90 via-charcoal-900 to-charcoal-950 p-4 shadow-glow-lg"
      role="status"
      aria-live="polite"
    >
      <div className="flex items-start gap-3">
        <div className="grid h-12 w-12 shrink-0 place-items-center rounded-xl bg-gradient-to-br from-ember-400 to-ember-600 text-2xl shadow-glow">
          {achievement.emoji}
        </div>
        <div className="min-w-0">
          <div className="text-[10px] font-bold uppercase tracking-widest text-ember-300">
            Achievement unlocked
          </div>
          <div className="mt-0.5 text-base font-bold text-white">
            {achievement.title}
          </div>
          <div className="mt-1 text-xs text-white/60">{achievement.desc}</div>
        </div>
      </div>
    </motion.div>
  );
}