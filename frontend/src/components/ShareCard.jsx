import { forwardRef } from "react";
import { severityForScore } from "../utils/score.js";
import { CATEGORY_LABEL } from "../data/categories.js";

/**
 * Fixed-size share card (1200×630) designed for PNG export.
 *
 * Intentionally uses only inline styles / plain CSS — no Tailwind classes,
 * no framer-motion, no backdrop blur — because html-to-image renders those
 * inconsistently across browsers.
 *
 * Attach a ref to grab the DOM node for export.
 */
const ShareCard = forwardRef(function ShareCard({ entry }, ref) {
  const r = entry?.result || {};
  const score = Math.round(r.score ?? 0);
  const sev = severityForScore(score);
  const recovery = Math.round(r.recovery_probability ?? 0);
  const diagnosis = r.diagnosis || "";
  const commentary = r.funny_commentary || "";
  const category = CATEGORY_LABEL[r.category] || "🔥 Other";

  // Palette based on score
  const [c1, c2] =
    score >= 86 ? ["#ff3b30", "#7f0f0a"]
    : score >= 71 ? ["#ff5c16", "#7a1f00"]
    : score >= 51 ? ["#ffa874", "#c72b0c"]
    : score >= 31 ? ["#ffd166", "#ff803c"]
    : ["#86efac", "#22c55e"];

  return (
    <div
      ref={ref}
      style={{
        width: "1200px",
        height: "630px",
        display: "flex",
        fontFamily:
          "'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif",
        background:
          "radial-gradient(900px 500px at 15% -10%, rgba(255,92,22,0.18), transparent 60%), radial-gradient(700px 400px at 110% 110%, rgba(255,140,60,0.14), transparent 60%), #0a0a0d",
        color: "#f5f5f7",
        padding: "56px",
        boxSizing: "border-box",
        position: "relative",
        overflow: "hidden",
      }}
    >
      {/* Subtle ember glow */}
      <div
        style={{
          position: "absolute",
          top: "-80px",
          left: "-80px",
          width: "360px",
          height: "360px",
          borderRadius: "50%",
          background: `${c1}22`,
          filter: "blur(80px)",
        }}
      />
      <div
        style={{
          position: "absolute",
          bottom: "-100px",
          right: "-80px",
          width: "400px",
          height: "400px",
          borderRadius: "50%",
          background: `${c2}33`,
          filter: "blur(100px)",
        }}
      />

      {/* LEFT — Score hero */}
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          width: "440px",
          position: "relative",
          zIndex: 1,
        }}
      >
        <div>
          <div
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: "10px",
              padding: "8px 16px",
              borderRadius: "999px",
              border: "1px solid rgba(255,255,255,0.12)",
              background: "rgba(255,255,255,0.04)",
              fontSize: "15px",
              letterSpacing: "0.1em",
              textTransform: "uppercase",
              color: "rgba(255,255,255,0.7)",
            }}
          >
            <span>🔥</span>
            <span>Am I Cooked?</span>
          </div>

          <div
            style={{
              marginTop: "40px",
              fontSize: "150px",
              fontWeight: 900,
              letterSpacing: "-0.04em",
              lineHeight: 1,
              background: `linear-gradient(135deg, ${c1}, ${c2})`,
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
              backgroundClip: "text",
            }}
          >
            {score}%
          </div>

          <div
            style={{
              marginTop: "16px",
              fontSize: "28px",
              fontWeight: 800,
              letterSpacing: "0.05em",
              color: c1,
            }}
          >
            {sev.emoji} {sev.pretty}
          </div>
        </div>

        <div style={{ fontSize: "16px", color: "rgba(255,255,255,0.55)" }}>
          {category}
        </div>
      </div>

      {/* RIGHT — Diagnosis + recovery */}
      <div
        style={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          paddingLeft: "48px",
          position: "relative",
          zIndex: 1,
        }}
      >
        <div>
          {diagnosis && (
            <div
              style={{
                fontSize: "26px",
                lineHeight: 1.35,
                fontWeight: 600,
                color: "rgba(255,255,255,0.95)",
              }}
            >
              “{diagnosis}”
            </div>
          )}

          {commentary && (
            <div
              style={{
                marginTop: "20px",
                fontSize: "17px",
                lineHeight: 1.5,
                fontStyle: "italic",
                color: "rgba(255,168,116,0.9)",
              }}
            >
              {commentary}
            </div>
          )}
        </div>

        <div>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "baseline",
              marginBottom: "12px",
            }}
          >
            <div
              style={{
                fontSize: "13px",
                letterSpacing: "0.15em",
                textTransform: "uppercase",
                color: "rgba(255,255,255,0.5)",
              }}
            >
              Recovery chance
            </div>
            <div
              style={{
                fontSize: "22px",
                fontWeight: 800,
                color: "#86efac",
              }}
            >
              {recovery}%
            </div>
          </div>

          <div
            style={{
              height: "10px",
              borderRadius: "999px",
              background: "rgba(255,255,255,0.08)",
              overflow: "hidden",
            }}
          >
            <div
              style={{
                width: `${recovery}%`,
                height: "100%",
                background: "linear-gradient(90deg, #86efac, #22c55e)",
              }}
            />
          </div>

          <div
            style={{
              marginTop: "28px",
              paddingTop: "20px",
              borderTop: "1px solid rgba(255,255,255,0.08)",
              fontSize: "14px",
              color: "rgba(255,255,255,0.45)",
              letterSpacing: "0.02em",
            }}
          >
            am-i-cooked · tell us your problem. we'll tell you how cooked you are.
          </div>
        </div>
      </div>
    </div>
  );
});

export default ShareCard;