import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Flame, Home, History, Trophy } from "lucide-react";

export default function NotFound() {
  return (
    <section className="mx-auto flex max-w-2xl flex-col items-center px-4 py-20 text-center">
      <motion.div
        initial={{ scale: 0.7, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.5, ease: "backOut" }}
        className="relative grid h-24 w-24 place-items-center"
      >
        <div className="absolute inset-0 animate-flicker rounded-full bg-gradient-to-br from-ember-400 to-ember-700 opacity-30 blur-2xl" />
        <div className="grid h-20 w-20 place-items-center rounded-full bg-gradient-to-br from-ember-400 to-ember-700 shadow-glow-lg">
          <Flame size={36} className="text-white" />
        </div>
      </motion.div>

      <motion.h1
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="mt-8 font-display text-5xl font-extrabold sm:text-7xl"
      >
        🔥 404
      </motion.h1>

      <motion.p
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.15 }}
        className="mt-4 max-w-md text-white/70"
      >
        This page is so cooked it no longer exists. Nothing left but ash.
      </motion.p>

      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="mt-10 flex flex-wrap items-center justify-center gap-3"
      >
        <Link to="/" className="btn-primary">
          <Home size={16} /> Go home
        </Link>
        <Link to="/analyze" className="btn-ghost">
          <Flame size={16} /> Analyze something
        </Link>
        <Link to="/history" className="btn-ghost">
          <History size={16} /> History
        </Link>
        <Link to="/achievements" className="btn-ghost">
          <Trophy size={16} /> Achievements
        </Link>
      </motion.div>
    </section>
  );
}