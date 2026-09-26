export default function SectionTitle({ icon, children, hint }) {
  return (
    <div className="mb-3 flex items-center justify-between gap-3">
      <h3 className="flex items-center gap-2 text-sm font-semibold uppercase tracking-wider text-white/70">
        {icon}
        {children}
      </h3>
      {hint && <span className="text-xs text-white/40">{hint}</span>}
    </div>
  );
}