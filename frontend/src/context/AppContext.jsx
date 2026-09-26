import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import toast from "react-hot-toast";
import {
  getHistory,
  addHistory,
  deleteHistory,
  clearHistory,
  getAchievements,
  unlockAchievement,
  getStats,
  bumpStat,
  setStat,
} from "../services/storage.js";
import { ACHIEVEMENT_MAP } from "../data/achievements.js";
import AchievementToast from "../components/AchievementToast.jsx";

const AppContext = createContext(null);

export function AppProvider({ children }) {
  const [history, setHistoryState] = useState([]);
  const [achievements, setAchievementsState] = useState([]);
  const [stats, setStatsState] = useState({ chaosUses: 0, analyses: 0, bestDrop: 0 });

  useEffect(() => {
    setHistoryState(getHistory());
    setAchievementsState(getAchievements());
    setStatsState(getStats());
  }, []);

  const pushHistory = useCallback((entry) => {
    addHistory(entry);
    setHistoryState(getHistory());
  }, []);

  const removeHistory = useCallback((id) => {
    deleteHistory(id);
    setHistoryState(getHistory());
  }, []);

  const wipeHistory = useCallback(() => {
    clearHistory();
    setHistoryState([]);
  }, []);

  const unlock = useCallback((id) => {
    const isNew = unlockAchievement(id);
    if (isNew) {
      setAchievementsState(getAchievements());
      const meta = ACHIEVEMENT_MAP[id];
      if (meta) {
        toast.custom(
          (t) => <AchievementToast achievement={meta} t={t} />,
          { duration: 4500, position: "top-right" }
        );
      }
    }
    return isNew;
  }, []);

  const bump = useCallback((key, delta = 1) => {
    const next = bumpStat(key, delta);
    setStatsState(next);
    return next;
  }, []);

  const updateStat = useCallback((key, value) => {
    const next = setStat(key, value);
    setStatsState(next);
    return next;
  }, []);

  const value = useMemo(
    () => ({
      history,
      achievements,
      stats,
      pushHistory,
      removeHistory,
      wipeHistory,
      unlock,
      bump,
      updateStat,
    }),
    [history, achievements, stats, pushHistory, removeHistory, wipeHistory, unlock, bump, updateStat]
  );

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

export function useApp() {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error("useApp must be used within <AppProvider>");
  return ctx;
}