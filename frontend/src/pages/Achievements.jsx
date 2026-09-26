import { useMemo } from "react";
import { motion } from "framer-motion";
import { Trophy, Lock } from "lucide-react";
import { ACHIEVEMENTS } from "../data/achievements.js";
import { useApp } from "../context/AppContext.jsx";

export default function Achievements() {
  const { achievements } = useApp();
  const unlocked = useMemo(() => new Set(achievements), [achievements]);
  const total = ACHIEVEMENTS.length;
  const count = ACHIEVEMENTS.filter((a) => unlocked.has(a.id)).length;
  const pct = total ? Math.round((count / total) * 100) : 0;

  return (
    <section className="mx-auto max-w-5xl px-4 py-10 sm:py-14">
      {/* Header */}
      <div className="mb-8 text-center">
        <div className="mx-auto mb-4 grid h-16 w-16 place-items-center rounded-2xl bg-gradient-to-br from-ember-400 to-ember-700 shadow-glow-lg">
          <Trophy size={28} className="text-white" />
        </div>
        <h1 className="font-display text-3xl font-extrabold sm:text-4xl">
          Achievements
        </h1>
        <p className="mt-2 text-white/60">
          {count} of {total} unlocked
        </p>

        <div className="mx-auto mt-6 h-2 w-full max-w-md overflow-hidden rounded-full bg-white/10">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${pct}%` }}
            transition={{ duration: 0.8, ease: "easeOut" }}
            className="h-full bg-gradient-to-r from-ember-400 to-ember-600"
          />
        </div>
      </div>

      {/* Grid */}
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {ACHIEVEMENTS.map((a, i) => {
          const isUnlocked = unlocked.has(a.id);
          return (
            <motion.div
              key={a.id}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: i * 0.03 }}
              className={[
                "relative overflow-hidden rounded-2xl border p-5 transition-all",
                isUnlocked
                  ? "border-ember-500/40 bg-gradient-to-br from-ember-950/40 via-charcoal-900 to-charcoal-950 shadow-glow"
                  : "border-white/10 bg-white/[0.02]",
              ].join(" ")}
            >
              {isUnlocked && (
                <div
                  aria-hidden="true"
                  className="pointer-events-none absolute -right-6 -top-6 h-24 w-24 rounded-full bg-ember-500/20 blur-2xl"
                />
              )}

              <div className="relative flex items-start gap-3">
                <div
                  className={[
                    "grid h-12 w-12 shrink-0 place-items-center rounded-xl text-2xl",
                    isUnlocked
                      ? "bg-gradient-to-br from-ember-400 to-ember-600 shadow-glow"
                      : "bg-white/5 text-white/30",
                  ].join(" ")}
                >
                  {isUnlocked ? a.emoji : <Lock size={20} />}
                </div>
                <div className="min-w-0">
                  <div
                    className={[
                      "text-base font-bold",
                      isUnlocked ? "text-white" : "text-white/40",
                    ].join(" ")}
                  >
                    {a.title}
                  </div>
                  <div
                    className={[
                      "mt-1 text-xs",
                      isUnlocked ? "text-white/70" : "text-white/35",
                    ].join(" ")}
                  >
                    {a.desc}
                  </div>
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>

      {count === total && (
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-10 rounded-2xl border border-ember-500/40 bg-ember-500/5 p-6 text-center"
        >
          <div className="text-4xl">🏆</div>
          <h3 className="mt-3 font-display text-xl font-extrabold">
            All achievements unlocked
          </h3>
          <p className="mt-1 text-sm text-white/60">
            You've cooked more than the average user. We're not sure whether to
            congratulate or console you.
          </p>
        </motion.div>
      )}
    </section>
  );
}