import { useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { AlertTriangle, X } from "lucide-react";

export default function ConfirmDialog({
  open,
  title = "Are you sure?",
  message,
  confirmLabel = "Confirm",
  cancelLabel = "Cancel",
  danger = false,
  onConfirm,
  onCancel,
}) {
  const ref = useRef(null);

  // Close on Escape
  useEffect(() => {
    if (!open) return;
    function onKey(e) {
      if (e.key === "Escape") onCancel?.();
    }
    window.addEventListener("keydown", onKey);
    // Focus the dialog for keyboard users
    ref.current?.focus();
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onCancel]);

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.15 }}
          className="fixed inset-0 z-50 grid place-items-center bg-black/60 p-4 backdrop-blur-sm"
          onClick={onCancel}
          role="presentation"
        >
          <motion.div
            ref={ref}
            tabIndex={-1}
            initial={{ opacity: 0, y: 12, scale: 0.96 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 12, scale: 0.96 }}
            transition={{ duration: 0.2 }}
            className="w-full max-w-md rounded-2xl border border-white/10 bg-charcoal-900 p-6 shadow-glow-lg outline-none"
            onClick={(e) => e.stopPropagation()}
            role="dialog"
            aria-modal="true"
            aria-labelledby="confirm-title"
          >
            <div className="flex items-start justify-between gap-4">
              <div className="flex items-start gap-3">
                {danger && (
                  <span className="mt-0.5 grid h-8 w-8 shrink-0 place-items-center rounded-xl bg-red-500/15 text-red-300">
                    <AlertTriangle size={16} />
                  </span>
                )}
                <div>
                  <h3 id="confirm-title" className="text-lg font-semibold">
                    {title}
                  </h3>
                  {message && (
                    <p className="mt-1 text-sm text-white/60">{message}</p>
                  )}
                </div>
              </div>
              <button
                onClick={onCancel}
                className="rounded-lg p-1 text-white/50 hover:bg-white/5 hover:text-white"
                aria-label="Close"
              >
                <X size={16} />
              </button>
            </div>

            <div className="mt-6 flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
              <button onClick={onCancel} className="btn-ghost">
                {cancelLabel}
              </button>
              <button
                onClick={onConfirm}
                className={
                  danger
                    ? "inline-flex items-center justify-center gap-2 rounded-xl bg-red-500/90 px-4 py-2 text-sm font-semibold text-white hover:bg-red-500"
                    : "btn-primary"
                }
              >
                {confirmLabel}
              </button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}