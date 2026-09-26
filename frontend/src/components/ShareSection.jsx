import { useRef, useState } from "react";
import { motion } from "framer-motion";
import toast from "react-hot-toast";
import { Download, Copy, Loader2, Share2 } from "lucide-react";
import ShareCard from "./ShareCard.jsx";
import { downloadPngAsImage, formatShareText, copyToClipboard } from "../utils/share.js";

export default function ShareSection({ entry }) {
  const cardRef = useRef(null);
  const [busy, setBusy] = useState(false);
  const [copied, setCopied] = useState(false);

  async function onDownload() {
    if (busy) return;
    setBusy(true);
    try {
      const score = Math.round(entry?.result?.score ?? 0);
      await downloadPngAsImage({
        node: cardRef.current,
        filename: `am-i-cooked-${score}.png`,
      });
      toast.success("Image saved 🔥", { duration: 3000 });
    } catch (err) {
      console.error(err);
      toast.error("Image export failed. Try again.");
    } finally {
      setBusy(false);
    }
  }

  async function onCopy() {
    const text = formatShareText(entry);
    const ok = await copyToClipboard(text);
    if (ok) {
      setCopied(true);
      toast.success("Copied to clipboard 📋", { duration: 2500 });
      setTimeout(() => setCopied(false), 2000);
    } else {
      toast.error("Copy failed. Your browser blocked it.");
    }
  }

  return (
    <motion.section
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="rounded-3xl border border-white/10 bg-white/[0.03] p-6 sm:p-8"
    >
      <div className="mb-1 flex items-center gap-2 text-ember-300">
        <Share2 size={16} />
        <span className="text-xs font-semibold uppercase tracking-widest">
          Share this result
        </span>
      </div>
      <h3 className="font-display text-2xl font-extrabold sm:text-3xl">
        📸 Send it to your friends
      </h3>
      <p className="mt-1 text-sm text-white/60">
        Download a card or copy a text version. Both work offline.
      </p>

      {/* Live preview: scaled-down version of the actual render target */}
      <div className="mt-6 overflow-hidden rounded-2xl border border-white/10">
        <div
          className="relative mx-auto"
          style={{
            // The real card is 1200×630; scale it for the preview.
            aspectRatio: "1200 / 630",
            width: "100%",
          }}
        >
          <div
            className="absolute left-0 top-0 origin-top-left"
            style={{
              transform: "scale(var(--preview-scale, 0.5))",
              width: "1200px",
              height: "630px",
              // measure container / 1200 in JS below
            }}
            ref={(node) => {
              if (node && node.parentElement) {
                const parentWidth = node.parentElement.clientWidth;
                node.style.setProperty(
                  "--preview-scale",
                  String(parentWidth / 1200)
                );
              }
            }}
          >
            <ShareCard entry={entry} />
          </div>
        </div>
      </div>

      <div className="mt-6 flex flex-wrap gap-3">
        <button
          onClick={onDownload}
          disabled={busy}
          className="btn-primary"
          aria-label="Download share image"
        >
          {busy ? (
            <>
              <Loader2 size={16} className="animate-spin" /> Generating…
            </>
          ) : (
            <>
              <Download size={16} /> Download image
            </>
          )}
        </button>
        <button
          onClick={onCopy}
          className="btn-ghost"
          aria-label="Copy result as text"
        >
          {copied ? (
            <>
              <Copy size={16} /> Copied!
            </>
          ) : (
            <>
              <Copy size={16} /> Copy text
            </>
          )}
        </button>
      </div>

      {/* Off-screen render target for PNG export */}
      <div
        aria-hidden="true"
        style={{
          position: "fixed",
          left: "-99999px",
          top: 0,
          pointerEvents: "none",
          opacity: 0,
        }}
      >
        <ShareCard ref={cardRef} entry={entry} />
      </div>
    </motion.section>
  );
}