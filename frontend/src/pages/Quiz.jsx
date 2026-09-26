import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import toast from "react-hot-toast";
import { ArrowLeft, ArrowRight, Flame, Check } from "lucide-react";
import clsx from "clsx";

import { QUIZ_QUESTIONS } from "../data/quiz.js";
import { scoreQuiz, buildQuizSituation } from "../utils/quizScoring.js";
import { fallbackAnalysis } from "../utils/fallback.js";
import { useApp } from "../context/AppContext.jsx";
import { uid } from "../utils/format.js";

export default function Quiz() {
  const navigate = useNavigate();
  const { pushHistory, unlock, bump } = useApp();

  const [step, setStep] = useState(0);
  const [answers, setAnswers] = useState(() => ({
    time: null,
    prep: QUIZ_QUESTIONS[1].default,
    serious: QUIZ_QUESTIONS[2].default,
    proc: QUIZ_QUESTIONS[3].default,
  }));
  const [direction, setDirection] = useState(1); // 1 forward, -1 back

  const total = QUIZ_QUESTIONS.length;
  const current = QUIZ_QUESTIONS[step];
  const isLast = step === total - 1;
  const canAdvance = useMemo(() => {
    if (current.kind === "single") return answers[current.id] !== null;
    return true;
  }, [current, answers]);

  function setAnswer(id, value) {
    setAnswers((prev) => ({ ...prev, [id]: value }));
  }

  function next() {
    if (!canAdvance) return;
    if (!isLast) {
      setDirection(1);
      setStep((s) => s + 1);
    } else {
      finish();
    }
  }

  function back() {
    if (step === 0) {
      navigate("/analyze");
      return;
    }
    setDirection(-1);
    setStep((s) => s - 1);
  }

  function finish() {
    const score = scoreQuiz(answers);
    const situation = buildQuizSituation(answers);

    // Reuse the local fallback to build a full result envelope
    const base = fallbackAnalysis(situation, "other");
    const result = {
      ...base,
      score,
      recovery_probability: Math.max(5, Math.min(95, 100 - score + 20)),
      demo_mode: true,
      source: "quiz",
    };

    const entry = {
      id: uid(),
      createdAt: Date.now(),
      situation,
      category: "other",
      result,
      source: "quiz",
    };
    pushHistory(entry);
    bump("analyses", 1);

    // Achievements
    if (result.score <= 10) unlock("barely_alive");
    if (result.score >= 51 && result.score <= 70) unlock("medium_rare");
    if (result.score >= 86) unlock("deeply_cooked");

    toast.success("Quiz complete. Preparing your verdict…", { icon: "🔥" });
    navigate(`/result/${entry.id}`);
  }

  return (
    <section className="mx-auto max-w-2xl px-4 py-10 sm:py-14">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <h1 className="font-display text-2xl font-extrabold sm:text-3xl">
            🔥 How Cooked Are You?
          </h1>
          <span className="text-sm text-white/50 tabular-nums">
            {step + 1} / {total}
          </span>
        </div>
        <div className="mt-4 h-1.5 w-full overflow-hidden rounded-full bg-white/10">
          <motion.div
            className="h-full bg-gradient-to-r from-ember-400 to-ember-600"
            initial={false}
            animate={{ width: `${((step + (canAdvance ? 1 : 0)) / total) * 100}%` }}
            transition={{ duration: 0.35, ease: "easeOut" }}
          />
        </div>
      </div>

      {/* Question */}
      <div className="relative min-h-[340px]">
        <AnimatePresence mode="wait" custom={direction}>
          <motion.div
            key={current.id}
            custom={direction}
            initial={{ opacity: 0, x: direction > 0 ? 40 : -40 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: direction > 0 ? -40 : 40 }}
            transition={{ duration: 0.3, ease: "easeOut" }}
            className="rounded-3xl border border-white/10 bg-white/[0.03] p-6 sm:p-8"
          >
            <h2 className="font-display text-xl font-bold sm:text-2xl">
              {current.title}
            </h2>
            {current.subtitle && (
              <p className="mt-1 text-sm text-white/50">{current.subtitle}</p>
            )}

            {/* Single choice */}
            {current.kind === "single" && (
              <div className="mt-6 grid gap-2">
                {current.options.map((o) => {
                  const selected = answers[current.id] === o.value;
                  return (
                    <button
                      key={o.value}
                      onClick={() => setAnswer(current.id, o.value)}
                      className={clsx(
                        "flex items-center justify-between rounded-2xl border px-4 py-3 text-left transition-all",
                        selected
                          ? "border-ember-500/60 bg-ember-500/10 text-white"
                          : "border-white/10 bg-white/[0.02] hover:bg-white/[0.06]"
                      )}
                      aria-pressed={selected}
                    >
                      <span>{o.label}</span>
                      <span
                        className={clsx(
                          "grid h-6 w-6 place-items-center rounded-lg border",
                          selected
                            ? "border-ember-400 bg-ember-500 text-white"
                            : "border-white/15 text-transparent"
                        )}
                      >
                        <Check size={14} />
                      </span>
                    </button>
                  );
                })}
              </div>
            )}

            {/* Slider */}
            {current.kind === "slider" && (
              <div className="mt-8">
                <div className="mb-3 flex items-center justify-between">
                  <span className="text-sm text-white/50">{current.min}</span>
                  <span className="rounded-xl bg-ember-500/15 px-3 py-1 text-lg font-bold text-ember-300 tabular-nums">
                    {answers[current.id]}
                    {current.suffix || ""}
                  </span>
                  <span className="text-sm text-white/50">{current.max}</span>
                </div>
                <input
                  type="range"
                  min={current.min}
                  max={current.max}
                  step={current.step}
                  value={answers[current.id]}
                  onChange={(e) => setAnswer(current.id, Number(e.target.value))}
                  className="w-full accent-ember-500"
                  aria-label={current.title}
                />
                <div className="mt-2 flex justify-between text-xs text-white/40">
                  <span>
                    {current.id === "prep" ? "Absolutely nothing" : "Mild"}
                  </span>
                  <span>
                    {current.id === "prep" ? "Fully ready" : "Legendary"}
                  </span>
                </div>
              </div>
            )}
          </motion.div>
        </AnimatePresence>
      </div>

      {/* Nav */}
      <div className="mt-8 flex items-center justify-between gap-3">
        <button onClick={back} className="btn-ghost">
          <ArrowLeft size={16} />
          {step === 0 ? "Cancel" : "Back"}
        </button>

        <button
          onClick={next}
          disabled={!canAdvance}
          className="btn-primary"
        >
          {isLast ? (
            <>
              <Flame size={18} /> Calculate my cooked score
            </>
          ) : (
            <>
              Next <ArrowRight size={16} />
            </>
          )}
        </button>
      </div>
    </section>
  );
}