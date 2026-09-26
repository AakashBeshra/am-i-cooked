import { toPng } from "html-to-image";

/**
 * Renders a DOM node to a PNG and triggers a download.
 *
 * @param {Object} opts
 * @param {HTMLElement} opts.node      - The element to rasterize
 * @param {string}       opts.filename - Suggested filename
 * @param {number}       [opts.pixelRatio=2]
 */
export async function downloadPngAsImage({ node, filename, pixelRatio = 2 }) {
  if (!node) throw new Error("No node to render");
  const dataUrl = await toPng(node, {
    pixelRatio,
    cacheBust: true,
    backgroundColor: "#0a0a0d",
    skipFonts: false,
  });

  const link = document.createElement("a");
  link.download = filename || "am-i-cooked.png";
  link.href = dataUrl;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

/**
 * Formats a cooked result as a plain-text share string.
 */
export function formatShareText(entry) {
  const r = entry?.result || {};
  const score = Math.round(r.score ?? 0);
  const severity = (r.severity || "").replace(/_/g, " ");
  const diagnosis = r.diagnosis || "";
  const recovery = Math.round(r.recovery_probability ?? 0);
  const commentary = r.funny_commentary || "";

  const lines = [
    "🔥 AM I COOKED?",
    "",
    `${score}% — ${severity}`,
    diagnosis ? `“${diagnosis}”` : null,
    commentary ? `\n${commentary}` : null,
    "",
    `Recovery chance: ${recovery}%`,
    "",
    "→ Find out how cooked you are: am-i-cooked",
  ].filter(Boolean);

  return lines.join("\n");
}

/**
 * Copies text to the clipboard. Uses the modern API, falls back to
 * execCommand for older browsers / non-secure contexts.
 */
export async function copyToClipboard(text) {
  if (typeof navigator !== "undefined" && navigator.clipboard?.writeText) {
    await navigator.clipboard.writeText(text);
    return true;
  }
  // Fallback
  try {
    const ta = document.createElement("textarea");
    ta.value = text;
    ta.setAttribute("readonly", "");
    ta.style.position = "fixed";
    ta.style.top = "-9999px";
    document.body.appendChild(ta);
    ta.select();
    const ok = document.execCommand("copy");
    document.body.removeChild(ta);
    return ok;
  } catch {
    return false;
  }
}