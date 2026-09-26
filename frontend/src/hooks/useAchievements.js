import { useCallback } from "react";
import { ACHIEVEMENT_MAP } from "../data/achievements.js";
import { useApp } from "../context/AppContext.jsx";

/**
 * Thin wrapper around the AppContext's unlock method.
 * Returns the achievement metadata if it was newly unlocked, else null.
 *
 * Usage:
 *   const { unlock, unlockBatch } = useAchievements();
 *   const meta = unlock("max_cook");     // returns achievement or null
 *   unlockBatch(["escaped", "speedrun"]);
 */
export function useAchievements() {
  const { unlock: unlockFromCtx } = useApp();

  const unlock = useCallback(
    (id) => {
      const wasNew = unlockFromCtx(id);
      return wasNew ? ACHIEVEMENT_MAP[id] || null : null;
    },
    [unlockFromCtx]
  );

  const unlockBatch = useCallback(
    (ids = []) => {
      const newlyUnlocked = [];
      for (const id of ids) {
        const meta = unlock(id);
        if (meta) newlyUnlocked.push(meta);
      }
      return newlyUnlocked;
    },
    [unlock]
  );

  return { unlock, unlockBatch };
}