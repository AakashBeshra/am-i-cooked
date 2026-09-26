import { motion } from "framer-motion";
import { Sparkles } from "lucide-react";

export default function WhatHappensNext({ items }) {
  if (!items?.length) return null;

  return (
    <motion.section
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.05 }}
      className="rounded-3xl border border-white/10 bg-white/[0.03] p-6 sm:p-8"
    >
      <div className="mb-1 flex items-center gap-2 text-ember-300">
        <Sparkles size={16} />
        <span className="text-xs font-semibold uppercase tracking-widest">
          Entertainment only
        </span>
      </div>
      <h3 className="font-display text-2xl font-extrabold sm:text-3xl">
        🔮 What happens next?
      </h3>
      <p className="mt-1 text-sm text-white/60">
        A purely fictional prediction, generated for your amusement. Not real
        fortune-telling. Probably.
      </p>

      <ol className="mt-6 space-y-3">
        {items.map((it, i) => (
          <motion.li
            key={i}
            initial={{ opacity: 0, x: -6 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3, delay: 0.05 * i }}
            className="flex items-start gap-4 rounded-2xl border border-white/10 bg-charcoal-900/40 p-4"
          >
            <span className="grid h-8 w-8 shrink-0 place-items-center rounded-xl bg-ember-500/15 text-xs font-bold text-ember-300">
              {i + 1}
            </span>
            <div>
              <div className="text-sm font-semibold text-white/80">
                {it.when}
              </div>
              <div className="text-white/70">{it.what}</div>
            </div>
          </motion.li>
        ))}
      </ol>
    </motion.section>
  );
}