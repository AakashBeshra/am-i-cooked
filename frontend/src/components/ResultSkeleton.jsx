/**
 * Skeleton shown while the Result page loads its entry from localStorage.
 * Prevents the "Loading…" flash and makes the transition feel instant.
 */
export default function ResultSkeleton() {
  return (
    <section className="mx-auto max-w-4xl px-4 py-10 sm:py-14 animate-pulse">
      {/* Hero */}
      <div className="mx-auto h-8 w-72 rounded-lg bg-white/5" />
      <div className="mx-auto mt-3 h-4 w-40 rounded-lg bg-white/5" />

      {/* Meter circle */}
      <div className="mx-auto mt-8 grid h-64 w-64 place-items-center rounded-full bg-white/5" />

      {/* Action row */}
      <div className="mt-6 flex justify-center gap-3">
        <div className="h-11 w-40 rounded-2xl bg-white/5" />
        <div className="h-11 w-32 rounded-2xl bg-white/5" />
        <div className="h-11 w-32 rounded-2xl bg-white/5" />
      </div>

      {/* Cards */}
      <div className="mt-10 space-y-6">
        <div className="h-32 rounded-3xl bg-white/5" />
        <div className="grid gap-6 lg:grid-cols-2">
          <div className="h-48 rounded-3xl bg-white/5" />
          <div className="h-48 rounded-3xl bg-white/5" />
        </div>
        <div className="h-24 rounded-3xl bg-white/5" />
        <div className="h-56 rounded-3xl bg-white/5" />
      </div>
    </section>
  );
}