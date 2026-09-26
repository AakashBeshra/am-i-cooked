"""
Severity mapping. Signal-driven scoring now lives in `signals.py`.
"""
from __future__ import annotations

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