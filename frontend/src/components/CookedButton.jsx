import { motion } from "framer-motion";
import { Flame } from "lucide-react";
import clsx from "clsx";

export default function CookedButton({
  children = "ANALYZE MY SITUATION",
  onClick,
  disabled = false,
  loading = false,
  className = "",
  type = "button",
}) {
  return (
    <motion.button
      type={type}
      onClick={onClick}
      disabled={disabled || loading}
      whileHover={disabled ? undefined : { scale: 1.02 }}
      whileTap={disabled ? undefined : { scale: 0.97 }}
      className={clsx(
        "btn-primary text-base sm:text-lg tracking-wide",
        "w-full sm:w-auto",
        className
      )}
    >
      <Flame size={20} className={loading ? "animate-pulse" : "group-hover:rotate-12 transition-transform"} />
      <span>{loading ? "ANALYZING…" : children}</span>
    </motion.button>
  );
}