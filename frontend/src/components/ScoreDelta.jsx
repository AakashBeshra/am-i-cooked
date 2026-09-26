import { motion, AnimatePresence } from "framer-motion";
import { ArrowRight } from "lucide-react";

/**
 * Animated "87% → 72%" banner that appears briefly when the user fixes something.
 */
export default function ScoreDelta({ from, to, visible }) {
  if (from == null || to == null) return null;
  const improved = to < from;
  const delta = Math.abs(from - to);

  return (
    <AnimatePresence>
      {visible && (
        <motion.div
          initial={{ opacity: 0, y: -8, scale: 0.96 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: -8, scale: 0.96 }}
          transition={{ duration: 0.35, ease: "easeOut" }}
          className={[
            "mx-auto flex w-fit items-center gap-3 rounded-2xl border px-4 py-2 text-sm font-semibold backdrop-blur-xl",
            improved
              ? "border-emerald-500/40 bg-emerald-500/10 text-emerald-300"
              : "border-ember-500/40 bg-ember-500/10 text-ember-300",
          ].join(" ")}
        >
          <span className="tabular-nums">🔥 {Math.round(from)}%</span>
          <ArrowRight size={16} className="opacity-70" />
          <span className="tabular-nums">🔥 {Math.round(to)}%</span>
          <span className="ml-1 text-xs opacity-80">
            {improved ? `−${delta} pts` : `+${delta} pts`}
          </span>
        </motion.div>
      )}
    </AnimatePresence>
  );
}