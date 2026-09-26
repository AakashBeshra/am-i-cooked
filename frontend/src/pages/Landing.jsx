import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import {
  Flame, Brain, ShieldCheck, Dices, Trophy, History as HistoryIcon, Share2,
} from "lucide-react";
import { EXAMPLE_SCENARIOS } from "../data/scenarios.js";

const features = [
  { icon: Brain,        title: "AI Analysis",       desc: "Structured, validated AI response every time." },
  { icon: Flame,        title: "Cook Meter",        desc: "A dramatic animated meter that tells the truth." },
  { icon: ShieldCheck,  title: "Recovery Plan",     desc: "Real steps. Real priorities. Real chances." },
  { icon: Dices,        title: "Random Chaos",      desc: "Press a button. Regret a scenario." },
  { icon: Trophy,       title: "Achievements",      desc: "Collect badges for your spectacular failures." },
  { icon: HistoryIcon,  title: "History",           desc: "Every cooked moment, remembered forever." },
  { icon: Share2,       title: "Shareable Results", desc: "Download a card. Send it to your friends." },
];

const steps = [
  { n: "01", t: "Tell us what happened", d: "Describe the situation. No judgment. Probably." },
  { n: "02", t: "AI analyzes the situation", d: "We measure time, panic, prep, and vibes." },
  { n: "03", t: "Receive your Cooked Score", d: "0–100%. With reasons, risks, and reality." },
  { n: "04", t: "Follow the recovery plan", d: "Practical steps that actually help." },
];

export default function Landing() {
  return (
    <div>
      {/* HERO */}
      <section className="relative overflow-hidden">
        <div className="mx-auto max-w-5xl px-4 pt-16 pb-20 text-center sm:pt-24">
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="chip mx-auto"
          >
            <Flame size={14} className="text-ember-400" />
            AI-powered situation analysis
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.05 }}
            className="mt-6 font-display text-5xl font-extrabold tracking-tight sm:text-7xl"
          >
            🔥 Am I <span className="text-ember-400">Cooked</span>?
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="mx-auto mt-5 max-w-2xl text-lg text-white/70 sm:text-xl"
          >
            Tell us your problem. We'll tell you how cooked you are.
            <span className="block text-white/40 text-base mt-2">No judgment. Probably.</span>
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.15 }}
            className="mt-10 flex flex-col items-center justify-center gap-3 sm:flex-row"
          >
            <Link to="/analyze" className="btn-primary text-base sm:text-lg">
              <Flame size={20} />
              Analyze my situation
            </Link>
            <Link to="/quiz" className="btn-ghost">
              🧠 Take the quiz
            </Link>
            <Link to="/analyze?mode=chaos" className="btn-ghost">
              🎲 Random Chaos
            </Link>
          </motion.div>
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section className="mx-auto max-w-6xl px-4 py-16">
        <h2 className="text-center font-display text-3xl font-bold sm:text-4xl">
          How it works
        </h2>
        <div className="mt-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {steps.map((s) => (
            <div key={s.n} className="card">
              <div className="text-sm font-mono text-ember-400">{s.n}</div>
              <h3 className="mt-2 text-lg font-semibold">{s.t}</h3>
              <p className="mt-1 text-sm text-white/60">{s.d}</p>
            </div>
          ))}
        </div>
      </section>

      {/* EXAMPLE SCENARIOS */}
      <section className="mx-auto max-w-6xl px-4 py-16">
        <h2 className="text-center font-display text-3xl font-bold sm:text-4xl">
          Example scenarios
        </h2>
        <p className="mx-auto mt-3 max-w-xl text-center text-white/60">
          A tiny sample of the chaos this app has witnessed.
        </p>
        <div className="mt-10 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {EXAMPLE_SCENARIOS.map((s) => (
            <Link
              key={s}
              to={`/analyze?situation=${encodeURIComponent(s)}`}
              className="group card transition-all hover:border-ember-500/40 hover:bg-white/[0.07]"
            >
              <p className="text-white/80 group-hover:text-white">"{s}"</p>
              <p className="mt-3 text-xs text-ember-400 opacity-0 transition-opacity group-hover:opacity-100">
                Analyze this →
              </p>
            </Link>
          ))}
        </div>
      </section>

      {/* FEATURES */}
      <section className="mx-auto max-w-6xl px-4 py-16">
        <h2 className="text-center font-display text-3xl font-bold sm:text-4xl">
          Features
        </h2>
        <div className="mt-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {features.map(({ icon: Icon, title, desc }) => (
            <div key={title} className="card">
              <div className="grid h-10 w-10 place-items-center rounded-xl bg-ember-500/15 text-ember-400">
                <Icon size={18} />
              </div>
              <h3 className="mt-4 text-lg font-semibold">{title}</h3>
              <p className="mt-1 text-sm text-white/60">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="mx-auto max-w-4xl px-4 py-20">
        <div className="glass-strong rounded-3xl p-8 text-center shadow-glow sm:p-12">
          <h2 className="font-display text-3xl font-extrabold sm:text-5xl">
            Find out how cooked you are
          </h2>
          <p className="mx-auto mt-4 max-w-xl text-white/70">
            The oven is preheated. The analysis is free. Your dignity is optional.
          </p>
          <div className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row">
            <Link to="/analyze" className="btn-primary text-lg">
              <Flame size={20} />
              Start the analysis
            </Link>
            <Link to="/quiz" className="btn-ghost">
              🧠 Take the quiz
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}