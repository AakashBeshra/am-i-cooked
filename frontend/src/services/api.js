import { fallbackAnalysis } from "../utils/fallback.js";

// Use the env var if set (production), else fall back to the Vite dev proxy path.
const API_BASE = import.meta.env.VITE_API_BASE || "/api";

async function safeFetch(path, options = {}, timeoutMs = 20000) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const res = await fetch(`${API_BASE}${path}`, {
      ...options,
      signal: controller.signal,
      headers: {
        "Content-Type": "application/json",
        ...(options.headers || {}),
      },
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } finally {
    clearTimeout(timer);
  }
}

export async function analyzeSituation({ situation, category = "auto" }) {
  try {
    const data = await safeFetch("/analyze", {
      method: "POST",
      body: JSON.stringify({ situation, category }),
    });
    if (!data || typeof data.score !== "number") {
      throw new Error("Malformed AI response");
    }
    return { ...data, demo_mode: false };
  } catch (err) {
    console.warn("[api] analyze fallback:", err.message);
    return fallbackAnalysis(situation, category);
  }
}

export async function getWhatHappensNext({ situation, score }) {
  try {
    return await safeFetch("/whats-next", {
      method: "POST",
      body: JSON.stringify({ situation, score }),
    });
  } catch {
    return null;
  }
}

export async function getHealth() {
  try {
    return await safeFetch("/health", { method: "GET" }, 4000);
  } catch {
    return { status: "offline" };
  }
}