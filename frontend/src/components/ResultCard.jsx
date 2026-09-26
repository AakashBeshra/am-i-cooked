import { motion } from "framer-motion";
import {
  Flame, Activity, ShieldCheck, TrendingUp, Stethoscope, AlertTriangle,
  Timer, Lightbulb,
} from "lucide-react";
import { severityForScore } from "../utils/score.js";
import { CATEGORY_LABEL } from "../data/categories.js";
import SectionTitle from "./SectionTitle.jsx";

export default function ResultCard({ data }) {
  const severity = severityForScore(data.score);
  const reasons = Array.isArray(data.reasons) ? data.reasons : [];
  const risks = Array.isArray(data.risk_factors) ? data.risk_factors : [];
  const plan = Array.isArray(data.recovery_plan) ? data.recovery_plan : [];
  const emergency = Array.isArray(data.emergency_actions) ? data.emergency_actions : [];

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-6"
    >
      {/* Diagnosis */}
      <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-6 sm:p-8">
        <SectionTitle icon={<Stethoscope size={14} />}>Diagnosis</SectionTitle>
        <p className="text-lg text-white/90 sm:text-xl">
          {data.diagnosis || "No diagnosis available."}
        </p>
        {data.funny_commentary && (
          <p className="mt-3 text-sm italic text-ember-300/90">
            “{data.funny_commentary}”
          </p>
        )}
      </section>

      {/* Reasons + Risks */}
      <div className="grid gap-6 lg:grid-cols-2">
        <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
          <SectionTitle icon={<AlertTriangle size={14} />}>
            Why you're cooked
          </SectionTitle>
          {reasons.length === 0 ? (
            <p className="text-sm text-white/50">No specific reasons reported.</p>
          ) : (
            <ul className="space-y-2">
              {reasons.map((r, i) => (
                <li
                  key={i}
                  className="flex items-center gap-3 rounded-xl border border-white/5 bg-white/[0.02] px-3 py-2"
                >
                  <span className="text-lg">{r.emoji || "•"}</span>
                  <span className="text-sm text-white/80">{r.label}</span>
                </li>
              ))}
            </ul>
          )}
        </section>

        <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
          <SectionTitle icon={<Activity size={14} />}>Risk factors</SectionTitle>
          {risks.length === 0 ? (
            <p className="text-sm text-white/50">No notable risk factors.</p>
          ) : (
            <ul className="space-y-2">
              {risks.map((r, i) => (
                <li
                  key={i}
                  className="rounded-xl border border-white/5 bg-white/[0.02] px-3 py-2 text-sm text-white/80"
                >
                  {r}
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>

      {/* Recovery probability bar */}
      <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
        <SectionTitle icon={<TrendingUp size={14} />} hint={`${Math.round(data.recovery_probability ?? 0)}%`}>
          Recovery probability
        </SectionTitle>
        <div className="h-3 w-full overflow-hidden rounded-full bg-white/10">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${Math.max(0, Math.min(100, data.recovery_probability ?? 0))}%` }}
            transition={{ duration: 0.9, ease: "easeOut" }}
            className="h-full bg-gradient-to-r from-emerald-400 to-emerald-600"
          />
        </div>
      </section>

      {/* Recovery plan */}
      <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-6 sm:p-8">
        <SectionTitle icon={<ShieldCheck size={14} />}>Recovery plan</SectionTitle>
        {plan.length === 0 ? (
          <p className="text-sm text-white/50">No plan available.</p>
        ) : (
          <ol className="space-y-2">
            {plan.map((step, i) => (
              <li
                key={i}
                className="flex items-start gap-3 rounded-xl border border-white/5 bg-white/[0.02] px-3 py-2"
              >
                <span className="grid h-6 w-6 shrink-0 place-items-center rounded-lg bg-ember-500/15 text-xs font-bold text-ember-300">
                  {i + 1}
                </span>
                <span className="text-sm text-white/85">{step}</span>
              </li>
            ))}
          </ol>
        )}
      </section>

      {/* Emergency actions (compact) */}
      {emergency.length > 0 && (
        <section className="rounded-3xl border border-ember-500/30 bg-ember-500/[0.06] p-6 sm:p-8">
          <SectionTitle icon={<Timer size={14} />}>Emergency actions</SectionTitle>
          <ul className="grid gap-2 sm:grid-cols-2">
            {emergency.map((a, i) => (
              <li
                key={i}
                className="flex items-start gap-2 rounded-xl border border-white/5 bg-white/[0.03] px-3 py-2 text-sm text-white/85"
              >
                <Lightbulb size={14} className="mt-0.5 shrink-0 text-ember-300" />
                {a}
              </li>
            ))}
          </ul>
        </section>
      )}

      {/* Meta */}
      <div className="flex flex-wrap items-center gap-3 text-xs text-white/50">
        <span className="chip">
          <Flame size={12} className="text-ember-400" />
          {severity.pretty}
        </span>
        {data.category && (
          <span className="chip">{CATEGORY_LABEL[data.category] || data.category}</span>
        )}
        {typeof data.confidence === "number" && (
          <span className="chip">
            Confidence {Math.round(data.confidence * 100)}%
          </span>
        )}
        {data.demo_mode && (
          <span className="chip border-amber-500/40 text-amber-300">
            Demo Mode
          </span>
        )}
      </div>
    </motion.div>
  );
}