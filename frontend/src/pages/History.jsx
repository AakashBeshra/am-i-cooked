import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import toast from "react-hot-toast";
import { Trash2, Eye, Flame, History as HistoryIcon } from "lucide-react";

import { useApp } from "../context/AppContext.jsx";
import { formatDate, truncate } from "../utils/format.js";
import { severityForScore } from "../utils/score.js";
import { CATEGORY_LABEL } from "../data/categories.js";
import ConfirmDialog from "../components/ConfirmDialog.jsx";
import EmptyState from "../components/EmptyState.jsx";

export default function History() {
  const { history, removeHistory, wipeHistory } = useApp();
  const navigate = useNavigate();
  const [confirmClear, setConfirmClear] = useState(false);
  const [pendingDelete, setPendingDelete] = useState(null);

  if (history.length === 0) {
    return (
      <section className="mx-auto max-w-4xl px-4 py-16">
        <EmptyState
          emoji="🍳"
          title="No cooked moments yet"
          message="Your history is suspiciously clean. Let's fix that."
          action={
            <Link to="/analyze" className="btn-primary">
              <Flame size={16} /> Analyze a situation
            </Link>
          }
        />
      </section>
    );
  }

  function confirmDelete() {
    if (pendingDelete) {
      removeHistory(pendingDelete.id);
      toast.success("Deleted.");
      setPendingDelete(null);
    }
  }

  function confirmWipe() {
    wipeHistory();
    toast.success("History cleared.");
    setConfirmClear(false);
  }

  return (
    <section className="mx-auto max-w-5xl px-4 py-10 sm:py-14">
      <div className="mb-8 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="flex items-center gap-2 font-display text-3xl font-extrabold sm:text-4xl">
            <HistoryIcon size={26} className="text-ember-400" />
            History
          </h1>
          <p className="mt-1 text-sm text-white/50">
            {history.length} saved {history.length === 1 ? "analysis" : "analyses"}.
          </p>
        </div>
        <button
          onClick={() => setConfirmClear(true)}
          className="btn-ghost text-red-300 hover:bg-red-500/10"
        >
          <Trash2 size={16} /> Clear all
        </button>
      </div>

      {/* Desktop table */}
      <div className="hidden overflow-hidden rounded-2xl border border-white/10 sm:block">
        <table className="w-full text-left text-sm">
          <thead className="bg-white/[0.04] text-white/60">
            <tr>
              <th className="px-4 py-3 font-medium">Date</th>
              <th className="px-4 py-3 font-medium">Situation</th>
              <th className="px-4 py-3 font-medium">Score</th>
              <th className="px-4 py-3 font-medium">Category</th>
              <th className="px-4 py-3 text-right font-medium">Actions</th>
            </tr>
          </thead>
          <tbody>
            {history.map((h) => {
              const sev = severityForScore(h.result.score);
              return (
                <motion.tr
                  key={h.id}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ duration: 0.25 }}
                  className="border-t border-white/5 hover:bg-white/[0.03]"
                >
                  <td className="whitespace-nowrap px-4 py-3 text-white/70">
                    {formatDate(h.createdAt)}
                  </td>
                  <td className="px-4 py-3 text-white/85">
                    {truncate(h.situation, 70)}
                  </td>
                  <td className="px-4 py-3">
                    <span className={`font-semibold tabular-nums ${sev.tone}`}>
                      {Math.round(h.result.score)}%
                    </span>
                    <span className="ml-2 text-xs text-white/40">
                      {sev.pretty}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-white/60">
                    {CATEGORY_LABEL[h.category] || h.category || "—"}
                  </td>
                  <td className="whitespace-nowrap px-4 py-3 text-right">
                    <button
                      onClick={() => navigate(`/result/${h.id}`)}
                      className="mr-1 inline-flex items-center gap-1 rounded-lg px-2 py-1 text-xs text-white/70 hover:bg-white/10 hover:text-white"
                      aria-label="View result"
                    >
                      <Eye size={14} /> View
                    </button>
                    <button
                      onClick={() => setPendingDelete(h)}
                      className="inline-flex items-center gap-1 rounded-lg px-2 py-1 text-xs text-red-300 hover:bg-red-500/10"
                      aria-label="Delete result"
                    >
                      <Trash2 size={14} /> Delete
                    </button>
                  </td>
                </motion.tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Mobile cards */}
      <div className="space-y-3 sm:hidden">
        {history.map((h) => {
          const sev = severityForScore(h.result.score);
          return (
            <div
              key={h.id}
              className="rounded-2xl border border-white/10 bg-white/[0.03] p-4"
            >
              <div className="flex items-center justify-between text-xs text-white/50">
                <span>{formatDate(h.createdAt)}</span>
                <span className={`font-semibold ${sev.tone}`}>
                  {Math.round(h.result.score)}%
                </span>
              </div>
              <p className="mt-2 text-sm text-white/85">
                {truncate(h.situation, 100)}
              </p>
              <div className="mt-3 flex items-center justify-between">
                <span className="text-xs text-white/50">
                  {CATEGORY_LABEL[h.category] || h.category || "—"}
                </span>
                <div className="flex gap-1">
                  <button
                    onClick={() => navigate(`/result/${h.id}`)}
                    className="rounded-lg px-2 py-1 text-xs text-white/70 hover:bg-white/10"
                  >
                    View
                  </button>
                  <button
                    onClick={() => setPendingDelete(h)}
                    className="rounded-lg px-2 py-1 text-xs text-red-300 hover:bg-red-500/10"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Clear-all confirm */}
      <ConfirmDialog
        open={confirmClear}
        title="Clear entire history?"
        message="This cannot be undone. Every cooked moment will be forgotten."
        confirmLabel="Clear everything"
        danger
        onCancel={() => setConfirmClear(false)}
        onConfirm={confirmWipe}
      />

      {/* Delete-one confirm */}
      <ConfirmDialog
        open={!!pendingDelete}
        title="Delete this analysis?"
        message={
          pendingDelete
            ? truncate(pendingDelete.situation, 80)
            : undefined
        }
        confirmLabel="Delete"
        danger
        onCancel={() => setPendingDelete(null)}
        onConfirm={confirmDelete}
      />
    </section>
  );
}