export const ACHIEVEMENTS = [
  { id: "zero_cooked",    title: "Zero Cooked",                emoji: "🎯", desc: "Score 0%. Suspiciously responsible." },
  { id: "barely_alive",   title: "Barely Alive",               emoji: "🏆", desc: "Finish with a score under 10%." },
  { id: "medium_rare",    title: "Medium Rare",                emoji: "🔥", desc: "Land in the 51–70% range." },
  { id: "deeply_cooked",  title: "Beyond Repair",              emoji: "💀", desc: "Reach 86% or higher." },
  { id: "max_cook",       title: "Absolutely Finished",        emoji: "☠️", desc: "Achieve a perfect 100%." },
  { id: "academic",       title: "Academic Weapon",            emoji: "🧠", desc: "Get an Academic category analysis." },
  { id: "procrastinator", title: "Professional Procrastinator", emoji: "🤡", desc: "Use Random Chaos 3 times." },
  { id: "emergency",      title: "Emergency Mode Survivor",    emoji: "🚨", desc: "Trigger Emergency Mode." },
  { id: "escaped",        title: "Escaped the Oven",           emoji: "🛟", desc: "Drop your score by 30+ points." },
  { id: "speedrun",       title: "Speedrun Recovery",          emoji: "⚡", desc: "Drop your score by 30+ points in one click." },
];

export const ACHIEVEMENT_MAP = Object.fromEntries(
  ACHIEVEMENTS.map((a) => [a.id, a])
);