import { useEffect, useMemo, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

const EMOJIS = ["🔥", "💀", "☠️", "🎉", "⭐", "🧨", "🥳"];

export default function Confetti({ count = 40, durationMs = 4500 }) {
  const [visible, setVisible] = useState(true);
  const particles = useMemo(
    () =>
      Array.from({ length: count }).map((_, i) => ({
        id: i,
        emoji: EMOJIS[Math.floor(Math.random() * EMOJIS.length)],
        left: Math.random() * 100, // %
        delay: Math.random() * 0.8, // s
        duration: 2.2 + Math.random() * 1.6, // s
        rotate: (Math.random() - 0.5) * 360,
      })),
    [count]
  );

  useEffect(() => {
    const t = setTimeout(() => setVisible(false), durationMs);
    return () => clearTimeout(t);
  }, [durationMs]);

  return (
    <AnimatePresence>
      {visible && (
        <div
          aria-hidden="true"
          className="pointer-events-none fixed inset-0 z-40 overflow-hidden"
        >
          {particles.map((p) => (
            <motion.span
              key={p.id}
              initial={{ y: "-10vh", opacity: 1, rotate: 0 }}
              animate={{ y: "110vh", opacity: [1, 1, 0.8, 0], rotate: p.rotate }}
              transition={{
                duration: p.duration,
                delay: p.delay,
                ease: "easeIn",
              }}
              style={{
                position: "absolute",
                left: `${p.left}%`,
                fontSize: "28px",
                willChange: "transform",
              }}
            >
              {p.emoji}
            </motion.span>
          ))}
        </div>
      )}
    </AnimatePresence>
  );
}