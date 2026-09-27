import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { motion } from "framer-motion";
import toast from "react-hot-toast";
import { Dices, Wand2, Send } from "lucide-react";
import clsx from "clsx";

import { CATEGORIES } from "../data/categories.js";
import { EXAMPLE_SCENARIOS, pickChaosScenario } from "../data/scenarios.js";
import { detectTextEgg } from "../data/easterEggs.js";
import { analyzeSituation } from "../services/api.js";
import { fallbackAnalysis } from "../utils/fallback.js";
import { useApp } from "../context/AppContext.jsx";
import { uid } from "../utils/format.js";
import LoadingMessages from "../components/LoadingMessages.jsx";
import CookedButton from "../components/CookedButton.jsx";

export default function Analyze() {
  const [params, setParams] = useSearchParams();
  const navigate = useNavigate();
  const { pushHistory, unlock, bump } = useApp();

  const [situation, setSituation] = useState(params.get("situation") || "");
  const [category, setCategory] = useState("auto");
  const [loading, setLoading] = useState(false);
  const [eggMessage, setEggMessage] = useState(null);

  // Prefill chaos mode
  useEffect(() => {
    if (params.get("mode") === "chaos") {
      const chaos = pickChaosScenario();
      setSituation(chaos);
      setCategory("chaos");
      bump("chaosUses", 1);
      // strip the query so refresh doesn't re-trigger
      params.delete("mode");
      setParams(params, { replace: true });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const charCount = situation.length;
  const canSubmit = situation.trim().length >= 3 && !loading;

  const placeholder = useMemo(
    () => "Tell me what happened…",
    []
  );

  function onExample(example) {
    setSituation(example);
  }

  function onChaos() {
    const chaos = pickChaosScenario();
    setSituation(chaos);
    setCategory("chaos");
    bump("chaosUses", 1);
    toast("🎲 Chaos delivered.", { icon: "🔥" });
  }

  async function onSubmit(e) {
    e?.preventDefault?.();
    if (!canSubmit) return;

    const trimmed = situation.trim();

    // Easter egg check (subtle; does NOT block analysis)
    const egg = detectTextEgg(trimmed);
    if (egg) {
      setEggMessage(egg);
      toast(egg, { icon: "🥚", duration: 5000 });
    }

    setLoading(true);
    try {
      const result = await analyzeSituation({ situation: trimmed, category });

      // Local fallback if backend totally failed AND fallback also failed
      const safe = result && typeof result.score === "number"
        ? result
        : fallbackAnalysis(trimmed, category);

      // Score-based easter eggs
      if (safe.score === 100) {
        toast("☠️ CONGRATULATIONS. YOU HAVE ACHIEVED MAXIMUM COOK.", {
          duration: 6000,
          icon: "🏆",
        });
      } else if (safe.score === 0) {
        toast("Suspiciously responsible behavior detected.", {
          duration: 5000,
          icon: "🧐",
        });
      }

      const entry = {
        id: uid(),
        createdAt: Date.now(),
        situation: trimmed,
        category: safe.category || category,
        result: safe,
      };
      pushHistory(entry);
      bump("analyses", 1);

      // Achievements based on score
      if (safe.score === 0) unlock("zero_cooked");
      if (safe.score <= 10) unlock("barely_alive");
      if (safe.score >= 51 && safe.score <= 70) unlock("medium_rare");
      if (safe.score >= 86) unlock("deeply_cooked");
      if (safe.score >= 100) unlock("max_cook");
      if ((safe.category || category) === "academic") unlock("academic");

      // Navigate to result
      navigate(`/result/${entry.id}`);
    } catch (err) {
      console.error(err);
      toast.error("The oven lost power. Try again in a moment.");
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <section className="mx-auto max-w-3xl px-4 py-16">
        <LoadingMessages />
      </section>
    );
  }

  return (
    <section className="mx-auto max-w-3xl px-4 py-10 sm:py-16">
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        <h1 className="font-display text-3xl font-extrabold sm:text-5xl">
          Tell us what's going on.
        </h1>
        <p className="mt-3 text-white/60">No judgment. Probably.</p>

        <form onSubmit={onSubmit} className="mt-8">
          {/* Category picker */}
          <div className="mb-4">
            <label className="mb-2 block text-sm text-white/60">Category</label>
            <div className="flex flex-wrap gap-2">
              {CATEGORIES.map((c) => (
                <button
                  type="button"
                  key={c.id}
                  onClick={() => setCategory(c.id)}
                  className={clsx(
                    "chip transition-all",
                    category === c.id
                      ? "border-ember-500/60 bg-ember-500/15 text-white"
                      : "hover:bg-white/10"
                  )}
                >
                  <span>{c.emoji}</span>
                  <span>{c.label}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Textarea */}
          <div className="relative">
            <textarea
              value={situation}
              onChange={(e) => setSituation(e.target.value)}
              placeholder={placeholder}
              rows={5}
              maxLength={800}
              className="w-full resize-none rounded-2xl border border-white/10 bg-white/5 p-4 text-white placeholder-white/40 outline-none transition-colors focus:border-ember-500/60 focus:bg-white/[0.07]"
            />
            <div className="mt-1 flex items-center justify-between px-1 text-xs text-white/40">
              <span>{charCount}/800</span>
              {eggMessage && <span className="text-ember-400">{eggMessage}</span>}
            </div>
          </div>

          {/* Examples */}
          <div className="mt-4 flex flex-wrap gap-2">
            {EXAMPLE_SCENARIOS.slice(0, 4).map((ex) => (
              <button
                type="button"
                key={ex}
                onClick={() => onExample(ex)}
                className="chip text-white/60 hover:text-white"
              >
                {ex}
              </button>
            ))}
          </div>

          {/* Actions */}
          <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex gap-2">
              <button type="button" onClick={onChaos} className="btn-ghost">
                <Dices size={16} /> Random Chaos
              </button>
              <button
                type="button"
                onClick={() => { setSituation(""); setEggMessage(null); }}
                className="btn-ghost"
                aria-label="Clear input"
              >
                Clear
              </button>
            </div>
            <CookedButton type="submit" disabled={!canSubmit} loading={loading} />
          </div>
        </form>

        {/* Quiz entry point */}
        <div className="mt-10 rounded-2xl glass p-5">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-2 text-white/80">
              <Wand2 size={16} className="text-ember-400" />
              <span className="text-sm">
                Don't want to type? Take the <strong>How Cooked Are You?</strong> quiz.
              </span>
            </div>
            <Link to="/quiz" className="btn-ghost">
              Start quiz
            </Link>
          </div>
        </div>
      </motion.div>
    </section>
  );
}