export default function Footer() {
  return (
    <footer className="mt-16 border-t border-white/5">
      <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-3 px-4 py-8 text-sm text-white/50 sm:flex-row">
        <p>
          🔥 <span className="text-white/80 font-semibold">Am I Cooked?</span> — entertainment
          only. Not real advice. Probably.
        </p>
        <p className="text-xs">
          Built with React, FastAPI, and questionable life choices.
        </p>
      </div>
    </footer>
  );
}