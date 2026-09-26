const HISTORY_KEY = "aic_history_v1";
const ACHIEVEMENTS_KEY = "aic_achievements_v1";
const STATS_KEY = "aic_stats_v1";

function read(key, fallback) {
  try {
    const raw = localStorage.getItem(key);
    if (!raw) return fallback;
    return JSON.parse(raw);
  } catch {
    return fallback;
  }
}

function write(key, value) {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch (e) {
    console.warn("storage write failed", e);
  }
}

/* ---------- History ---------- */
export function getHistory() {
  return read(HISTORY_KEY, []);
}
export function addHistory(entry) {
  const list = getHistory();
  list.unshift(entry);
  write(HISTORY_KEY, list.slice(0, 100));
}
export function deleteHistory(id) {
  write(HISTORY_KEY, getHistory().filter((h) => h.id !== id));
}
export function clearHistory() {
  write(HISTORY_KEY, []);
}

/* ---------- Achievements ---------- */
export function getAchievements() {
  return read(ACHIEVEMENTS_KEY, []);
}
export function unlockAchievement(id) {
  const list = getAchievements();
  if (list.includes(id)) return false;
  list.push(id);
  write(ACHIEVEMENTS_KEY, list);
  return true;
}

/* ---------- Stats ---------- */
export function getStats() {
  return read(STATS_KEY, { chaosUses: 0, analyses: 0, bestDrop: 0 });
}
export function bumpStat(key, delta = 1) {
  const s = getStats();
  s[key] = (s[key] || 0) + delta;
  write(STATS_KEY, s);
  return s;
}
export function setStat(key, value) {
  const s = getStats();
  s[key] = value;
  write(STATS_KEY, s);
  return s;
}