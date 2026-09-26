"""
Deterministic heuristic scoring used by the MockProvider and as a
sanity check for LLM output.
"""
from __future__ import annotations

import re

SEVERITY_BY_SCORE = [
    (96, "BEYOND_REPAIR"),
    (86, "DEEPLY_COOKED"),
    (71, "HEAVILY_COOKED"),
    (51, "MEDIUM_RARE"),
    (31, "GETTING_WARM"),
    (11, "SLIGHTLY_COOKED"),
    (0,  "NOT_COOKED"),
]


def severity_for_score(score: int) -> str:
    score = max(0, min(100, int(score)))
    for threshold, label in SEVERITY_BY_SCORE:
        if score >= threshold:
            return label
    return "NOT_COOKED"


def heuristic_score(situation: str) -> int:
    """
    A deterministic scorer for the mock provider and for confidence checks.
    Mirrors the frontend `fallback.js` logic so demo mode feels consistent.

    Rule design:
    - Positive-context rules add to the score (things that make you more cooked).
    - A single negative-context rule subtracts (evidence of preparation).
      It must NOT fire on negated phrases like "haven't studied" — see the
      lookbehind guards below.
    """
    text = (situation or "").lower()
    score = 55

    # Positive (cooked) signals
    if re.search(r"tomorrow|tonight|in \d+ (min|hour)", text):
        score += 15
    if re.search(r"\b(exam|test|interview|deadline|due)\b", text):
        score += 10
    if re.search(r"haven'?t|didn'?t|not started|no idea|nothing", text):
        score += 10
    if re.search(r"\b(broke|payday)\b|no money|₹|\$", text):
        score += 8
    if re.search(r"accidentally|by mistake|oops", text):
        score += 6
    if re.search(r"i'?m fine|it'?s fine", text):
        score += 10

    # Negative (prepared) signal — only fire when NOT preceded by negation.
    # Lookbehinds are fixed-width (4 chars) as Python's `re` requires.
    if re.search(
        r"(?<!n't )(?<!not )\b(studied|prepared|ready|done)\b",
        text,
    ):
        score -= 25

    return max(3, min(99, score))