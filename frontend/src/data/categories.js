export const CATEGORIES = [
  { id: "auto",         label: "Auto Detect",     emoji: "🪄" },
  { id: "academic",     label: "Academic",        emoji: "🎓" },
  { id: "career",       label: "Career",          emoji: "💼" },
  { id: "relationship", label: "Relationships",   emoji: "❤️" },
  { id: "money",        label: "Money",           emoji: "💰" },
  { id: "life",         label: "Life",            emoji: "👨‍👩‍👧" },
  { id: "technology",   label: "Technology",      emoji: "🧑‍💻" },
  { id: "social",       label: "Social",          emoji: "🗣️" },
  { id: "time",         label: "Time Management", emoji: "⏰" },
  { id: "chaos",        label: "Random Chaos",    emoji: "🤡" },
  { id: "other",        label: "Other",           emoji: "🔥" },
];

export const CATEGORY_LABEL = Object.fromEntries(
  CATEGORIES.map((c) => [c.id, `${c.emoji} ${c.label}`])
);