import { Link, NavLink, useLocation } from "react-router-dom";
import { Flame, History, Trophy } from "lucide-react";

export default function Navbar() {
  const { pathname } = useLocation();

  const link = (to, label, Icon) => {
    const active = pathname === to;
    return (
      <NavLink
        to={to}
        className={({ isActive }) =>
          [
            "inline-flex items-center gap-1.5 rounded-xl px-3 py-2 text-sm transition-colors",
            isActive
              ? "bg-white/10 text-white"
              : "text-white/70 hover:text-white hover:bg-white/5",
          ].join(" ")
        }
        aria-current={active ? "page" : undefined}
      >
        <Icon size={16} />
        <span className="hidden sm:inline">{label}</span>
      </NavLink>
    );
  };

  return (
    <header className="sticky top-0 z-40 border-b border-white/5 bg-charcoal-950/70 backdrop-blur-xl">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
        <Link to="/" className="group inline-flex items-center gap-2">
          <span className="relative grid h-9 w-9 place-items-center rounded-xl bg-gradient-to-br from-ember-400 to-ember-700 shadow-glow">
            <Flame size={18} className="text-white" />
          </span>
          <span className="font-display text-lg font-extrabold tracking-tight">
            Am I <span className="text-ember-400">Cooked?</span>
          </span>
        </Link>

        <nav className="flex items-center gap-1">
          {link("/analyze", "Analyze", Flame)}
          {link("/history", "History", History)}
          {link("/achievements", "Achievements", Trophy)}
        </nav>
      </div>
    </header>
  );
}