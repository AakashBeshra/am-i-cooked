export const SEVERITY_LEVELS = [
  { min: 96, max: 100, label: "BEYOND_REPAIR",   pretty: "BEYOND REPAIR",   emoji: "☠️", tone: "text-red-400" },
  { min: 86, max: 95,  label: "DEEPLY_COOKED",   pretty: "DEEPLY COOKED",   emoji: "💀", tone: "text-red-400" },
  { min: 71, max: 85,  label: "HEAVILY_COOKED",  pretty: "HEAVILY COOKED",  emoji: "🔴", tone: "text-ember-400" },
  { min: 51, max: 70,  label: "MEDIUM_RARE",     pretty: "MEDIUM RARE",     emoji: "🟠", tone: "text-amber-400" },
  { min: 31, max: 50,  label: "GETTING_WARM",    pretty: "GETTING WARM",    emoji: "🟡", tone: "text-yellow-300" },
  { min: 11, max: 30,  label: "SLIGHTLY_COOKED", pretty: "SLIGHTLY COOKED", emoji: "🟢", tone: "text-emerald-400" },
  { min: 0,  max: 10,  label: "NOT_COOKED",      pretty: "NOT COOKED",      emoji: "🟢", tone: "text-emerald-400" },
];

export function severityForScore(score) {
  const s = Math.max(0, Math.min(100, Math.round(score)));
  return SEVERITY_LEVELS.find((l) => s >= l.min && s <= l.max) ?? SEVERITY_LEVELS.at(-1);
}

export function faceForScore(score) {
  if (score >= 96) return "☠️";
  if (score >= 86) return "💀";
  if (score >= 71) return "😰";
  if (score >= 51) return "😐";
  if (score >= 31) return "🙂";
  return "😎";
}

export function clamp(n, min = 0, max = 100) {
  return Math.max(min, Math.min(max, n));
}