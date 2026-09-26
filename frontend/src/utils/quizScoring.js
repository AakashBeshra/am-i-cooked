import { clamp } from "./score.js";
import { QUIZ_QUESTIONS } from "../data/quiz.js";

/**
 * Answers shape:
 * {
 *   time: "hours",
 *   prep: 20,
 *   serious: 6,
 *   proc: 7
 * }
 */
export function scoreQuiz(answers) {
  let weighted = 0;
  let totalWeight = 0;

  for (const q of QUIZ_QUESTIONS) {
    const raw = answers[q.id];
    let stress = 0;

    if (q.kind === "single") {
      const opt = q.options.find((o) => o.value === raw);
      stress = opt ? opt.stress : 0.5;
    } else {
      const num = typeof raw === "number" ? raw : q.default;
      stress = q.toStress(num);
    }

    stress = clamp(stress, 0, 1);
    weighted += stress * q.weight;
    totalWeight += q.weight;
  }

  const normalized = totalWeight > 0 ? weighted / totalWeight : 0.5;
  // Clamp to 3–99: 0 and 100 are reserved for the AI/fallback path
  return clamp(Math.round(normalized * 100), 3, 99);
}

export function buildQuizSituation(answers) {
  const timeQ = QUIZ_QUESTIONS.find((q) => q.id === "time");
  const timeLabel = timeQ.options.find((o) => o.value === answers.time)?.label || "unknown";

  return [
    `Self-assessment quiz.`,
    `Time available: ${timeLabel}.`,
    `Preparation: ${answers.prep ?? 0}%.`,
    `Seriousness: ${answers.serious ?? 5}/10.`,
    `Procrastination: ${answers.proc ?? 5}/10.`,
  ].join(" ");
}