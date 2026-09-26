import { useEffect, useMemo, useRef, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { motion } from "framer-motion";
import toast from "react-hot-toast";
import { RefreshCw, Wrench, Share2, Sparkles } from "lucide-react";

import CookMeter from "../components/CookMeter.jsx";
import ResultCard from "../components/ResultCard.jsx";
import EmergencyMode from "../components/EmergencyMode.jsx";
import WhatHappensNext from "../components/WhatHappensNext.jsx";
import ScoreDelta from "../components/ScoreDelta.jsx";
import ShareSection from "../components/ShareSection.jsx";
import ResultSkeleton from "../components/ResultSkeleton.jsx";
import Confetti from "../components/Confetti.jsx";

import { getHistory, addHistory } from "../services/storage.js";
import { useApp } from "../context/AppContext.jsx";
import { clamp, severityForScore } from "../utils/score.js";
import { uid } from "../utils/format.js";
import { fallbackAnalysis } from "../utils/fallback.js";

export default function Result() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { unlock, updateStat, bump } = useApp();

  const [entry, setEntry] = useState(null);
  const [notFound, setNotFound] = useState(false);
  const [delta, setDelta] = useState({ from: null, to: null, visible: false });
  const [fixing, setFixing] = useState(false);
  const deltaTimer = useRef(null);

  // Load entry from localStorage
  useEffect(() => {
    const list = getHistory();
    const found = list.find((h) => h.id === id);
    if (!found) {
      setNotFound(true);
      return;
    }
    setEntry(found);
  }, [id]);

  // Cleanup
  useEffect(() => () => clearTimeout(deltaTimer.current), []);

  const severity = useMemo(
    () => (entry ? severityForScore(entry.result.score) : null),
    [entry]
  );

  if (notFound) {
    return (
      <section className="mx-auto max-w-2xl px-4 py-24 text-center">
        <h1 className="text-3xl font-bold">That result has left the oven.</h1>
        <p className="mt-3 text-white/60">
          We couldn't find that analysis in your history.
        </p>
        <Link to="/analyze" className="btn-primary mt-8">
          Analyze a new situation
        </Link>
      </section>
    );
  }

  if (!entry) {
    return <ResultSkeleton />;
  }

  const currentScore = entry.result.score;

  function onReassess() {
    navigate("/analyze");
  }

  /**
   * "I FIXED SOMETHING" — nudges score down by a random 5–18 points,
   * shows the delta animation, unlocks achievements, saves new entry.
   */
  function onFixedSomething() {
    if (fixing) return;
    const previous = entry.result.score;
    // Bigger drops when score is high (more room to recover)
    const maxDrop = previous > 80 ? 22 : previous > 50 ? 16 : 10;
    const drop = 5 + Math.floor(Math.random() * (maxDrop - 4));
    const next = clamp(Math.round(previous - drop), 0, 100);

    // Re-run the local analyzer to regenerate a plausible narrative for the new score
    const rebuilt = fallbackAnalysis(entry.situation, entry.result.category || "other");
    const adjusted = {
      ...rebuilt,
      score: next,
      recovery_probability: clamp(rebuilt.recovery_probability + drop, 0, 99),
      funny_commentary:
        next >= 86
          ? "Bro is still charcoal. But charcoal with ambition."
          : next >= 60
          ? "The chicken is cooling. Slightly."
          : next >= 30
          ? "You're escaping the oven. Keep going."
          : "Suspiciously responsible behavior detected.",
    };

    // Update entry
    const updated = {
      ...entry,
      result: adjusted,
    };
    setEntry(updated);

    // Save to history (replace the same id)
    const list = getHistory();
    const idx = list.findIndex((h) => h.id === entry.id);
    if (idx >= 0) {
      list[idx] = updated;
      // storage helper only prepends; write raw
      try {
        localStorage.setItem("aic_history_v1", JSON.stringify(list));
      } catch { /* ignore */ }
    }

    // Show delta
    setDelta({ from: previous, to: next, visible: true });
    clearTimeout(deltaTimer.current);
    deltaTimer.current = setTimeout(() => {
      setDelta((d) => ({ ...d, visible: false }));
    }, 3200);

    // Track stats & achievements
    const totalDrop = previous - next;
    const prevBest = Number(localStorage.getItem("aic_best_drop") || 0);
    const bestDrop = Math.max(prevBest, totalDrop);
    localStorage.setItem("aic_best_drop", String(bestDrop));

    if (previous - next >= 30) {
      unlock("escaped");
    }
    if (totalDrop >= 30) {
      unlock("speedrun");
    }

    setFixing(true);
    setTimeout(() => setFixing(false), 700);

    toast(`🔥 ${previous}% → 🔥 ${next}%  —  keep going.`, { icon: "🛟" });
  }

  return (
    <section className="mx-auto max-w-4xl px-4 py-10 sm:py-14">
      {currentScore === 100 && <Confetti />}
      
      {/* HERO: title + meter */}
      <div className="text-center">
        <motion.h1
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="font-display text-3xl font-extrabold sm:text-5xl"
        >
          <span className="mr-2">{severity.emoji}</span>
          You are{" "}
          <span className="text-ember-400">{Math.round(currentScore)}%</span>{" "}
          cooked
        </motion.h1>
        <p className="mt-2 text-sm text-white/50">
          Severity: <span className={severity.tone}>{severity.pretty}</span>
        </p>
      </div>

      <div className="mt-8 flex justify-center">
        <CookMeter score={currentScore} />
      </div>

      <div className="mt-4">
        <ScoreDelta from={delta.from} to={delta.to} visible={delta.visible} />
      </div>

      {/* Action row */}
      <div className="mt-6 flex flex-wrap items-center justify-center gap-3">
        <button
          onClick={onFixedSomething}
          className="btn-primary"
          aria-label="I fixed something, recalculate my score"
          disabled={fixing}
        >
          <Wrench size={16} />
          {fixing ? "Recalculating…" : "I fixed something"}
        </button>
        <button
          onClick={() => {
            navigator.clipboard
              ?.writeText(
                `🔥 I'm ${Math.round(currentScore)}% cooked — ${severity.pretty}. Am I Cooked?`
              )
              .then(() => toast.success("Copied to clipboard"))
              .catch(() => toast.error("Copy failed"));
          }}
          className="btn-ghost"
        >
          <Share2 size={16} /> Quick share
        </button>
        <Link to="/analyze" className="btn-ghost">
          <RefreshCw size={16} /> Reassess
        </Link>
      </div>

      {/* Emergency mode */}
      {currentScore >= 80 && (
        <div className="mt-10">
          <EmergencyMode onReassess={onReassess} />
        </div>
      )}

      {/* Result card */}
      <div className="mt-10">
        <ResultCard data={entry.result} />
      </div>

      {/* What happens next */}
            {/* What happens next */}
      <div className="mt-10">
        <WhatHappensNext items={entry.result.what_happens_next} />
      </div>

      {/* Share */}
      <div className="mt-10">
        <ShareSection entry={entry} />
      </div>

      {/* Back link */}
      <div className="mt-10 flex justify-center">
        <Link to="/history" className="btn-ghost">
          <Sparkles size={16} /> See your history
        </Link>
      </div>
    </section>
  );
}