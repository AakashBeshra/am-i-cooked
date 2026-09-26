import { motion } from "framer-motion";

export default function EmptyState({ emoji = "🍳", title, message, action }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35 }}
      className="mx-auto max-w-lg rounded-3xl border border-white/10 bg-white/[0.03] p-10 text-center"
    >
      <div className="mb-4 text-5xl">{emoji}</div>
      <h3 className="text-xl font-semibold">{title}</h3>
      {message && <p className="mt-2 text-sm text-white/60">{message}</p>}
      {action && <div className="mt-6">{action}</div>}
    </motion.div>
  );
}