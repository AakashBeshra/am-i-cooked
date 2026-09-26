import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { LOADING_MESSAGES } from "../data/loadingMessages.js";

export default function LoadingMessages({ intervalMs = 1400 }) {
  const [index, setIndex] = useState(0);

  useEffect(() => {
    const id = setInterval(() => {
      setIndex((i) => (i + 1) % LOADING_MESSAGES.length);
    }, intervalMs);
    return () => clearInterval(id);
  }, [intervalMs]);

  const message = LOADING_MESSAGES[index];

  return (
    <div className="flex min-h-[40vh] w-full flex-col items-center justify-center">
      <div className="relative mb-8 grid h-24 w-24 place-items-center">
        <div className="absolute inset-0 animate-flicker rounded-full bg-gradient-to-br from-ember-400 to-ember-700 opacity-30 blur-2xl" />
        <div className="grid h-20 w-20 place-items-center rounded-full bg-gradient-to-br from-ember-400 to-ember-700 shadow-glow-lg">
          <span className="text-3xl">🔥</span>
        </div>
      </div>

      <AnimatePresence mode="wait">
        <motion.p
          key={message}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -8 }}
          transition={{ duration: 0.25 }}
          className="text-center text-lg text-white/90 sm:text-xl"
        >
          {message}
        </motion.p>
      </AnimatePresence>

      <div className="mt-8 h-1 w-56 overflow-hidden rounded-full bg-white/10">
        <motion.div
          className="h-full bg-gradient-to-r from-ember-400 to-ember-600"
          animate={{ x: ["-100%", "100%"] }}
          transition={{ repeat: Infinity, duration: 1.4, ease: "easeInOut" }}
          style={{ width: "60%" }}
        />
      </div>
    </div>
  );
}