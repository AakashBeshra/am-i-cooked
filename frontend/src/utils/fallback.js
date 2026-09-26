import { severityForScore } from "./score.js";

export function fallbackAnalysis(situation = "", category = "auto") {
  const text = (situation || "").toLowerCase();
  let score = 55;

  if (/tomorrow|tonight|in \d+ (min|hour)/.test(text)) score += 15;
  if (/\b(exam|test|interview|deadline|due)\b/.test(text)) score += 10;
  if (/haven'?t|didn'?t|not started|no idea|nothing/.test(text)) score += 10;
  if (/\b(broke|payday)\b|no money|₹|\$/.test(text)) score += 8;
  if (/accidentally|by mistake|oops/.test(text)) score += 6;
  if (/i'?m fine|it'?s fine/.test(text)) score += 10;

  // Only apply the "prepared" penalty when the word isn't negated.
  // (?<!n't )(?<!not ) — fixed-width lookbehinds, supported in modern V8.
  if (/(?<!n't )(?<!not )\b(studied|prepared|ready|done)\b/.test(text)) {
    score -= 25;
  }

  score = Math.max(3, Math.min(99, Math.round(score)));
  const sev = severityForScore(score);
  const recovery = Math.max(5, Math.min(95, 100 - score + 20));

  return {
    score,
    severity: sev.label,
    category: category === "auto" ? "other" : category,
    diagnosis:
      score >= 80
        ? "You're not completely doomed, but the oven is definitely preheating."
        : score >= 50
        ? "There's still time, but the clock is filing a complaint."
        : "Honestly? You might be okay. Suspicious.",
    reasons: [
      { emoji: "⏰", label: "Very little time remaining" },
      { emoji: "📚", label: "Low preparation detected" },
      { emoji: "😭", label: "Elevated panic signature" },
      { emoji: "📱", label: "Severe distraction risk" },
    ],
    risk_factors: [
      "Procrastination compounding",
      "Context-switching overhead",
      "Diminishing returns on cramming",
    ],
    recovery_probability: recovery,
    recovery_plan: [
      "Stop scrolling. Right now.",
      "Identify the single highest-priority task.",
      "Work 60–90 minutes without interruption.",
      "Short break. Water. Repeat.",
      "Do not attempt to solve everything simultaneously.",
    ],
    emergency_actions: [
      "Close all non-essential tabs.",
      "Put phone in another room.",
      "Set a 25-minute timer.",
      "Work on the ONE thing that matters most.",
    ],
    funny_commentary:
      score >= 86
        ? "Bro is not medium rare anymore. Bro is charcoal."
        : score >= 60
        ? "The oven is warm. The chicken is nervous."
        : "You might actually survive this. Don't get cocky.",
    what_happens_next: [
      { when: "In 10 minutes", what: "You will open YouTube." },
      { when: "In 25 minutes", what: "You will convince yourself one episode won't hurt." },
      { when: "In 2 hours", what: "You will suddenly discover motivation." },
      { when: "Tomorrow", what: "You will promise yourself this will never happen again." },
    ],
    confidence: 0.72,
    demo_mode: true,
  };
}