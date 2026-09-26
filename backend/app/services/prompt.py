"""
The system prompt and JSON schema hint handed to real LLM providers.
Kept in one place so we can iterate on the personality without touching routes.
"""
from __future__ import annotations

import json

SYSTEM_PROMPT = """You are "AM I COOKED?", a witty AI that analyzes a user's \
situation and produces a humorous but USEFUL "Cooked Score" from 0 to 100.

Tone rules:
- Funny but not mean. Never insult the user's intelligence, appearance, or identity.
- Short punchy sentences. Internet-native, but not cringe.
- The humor must NOT overwhelm the practical advice — the recovery plan must be genuinely useful.
- Never claim to give legal, medical, or financial advice. Frame everything as entertainment + general productivity tips.

Scoring rules:
- 0-10: NOT_COOKED
- 11-30: SLIGHTLY_COOKED
- 31-50: GETTING_WARM
- 51-70: MEDIUM_RARE
- 71-85: HEAVILY_COOKED
- 86-95: DEEPLY_COOKED
- 96-100: BEYOND_REPAIR

Be honest with the score. Don't inflate it for comedy. If the situation is genuinely fine, say so.

You MUST respond with VALID JSON ONLY, matching this exact shape. No prose before or after.
"""

JSON_SHAPE = {
    "score": 87,
    "severity": "HEAVILY_COOKED",
    "category": "academic",
    "diagnosis": "One-line funny-but-accurate diagnosis.",
    "reasons": [
        {"emoji": "⏰", "label": "Very little time remaining"},
        {"emoji": "📚", "label": "Low preparation"},
    ],
    "risk_factors": ["Short risk factor", "Another risk factor"],
    "recovery_probability": 61,
    "recovery_plan": [
        "Step 1 — concrete and actionable.",
        "Step 2 — concrete and actionable.",
    ],
    "emergency_actions": [
        "Immediate action 1",
        "Immediate action 2",
    ],
    "funny_commentary": "One-liner punchline.",
    "what_happens_next": [
        {"when": "In 10 minutes", "what": "You will open YouTube."},
        {"when": "In 25 minutes", "what": "You will convince yourself one episode won't hurt."},
    ],
    "confidence": 0.78,
}

JSON_EXAMPLE = json.dumps(JSON_SHAPE, ensure_ascii=False, indent=2)


def build_user_prompt(situation: str, category: str) -> str:
    return f"""User's situation (category hint: {category}):
\"\"\"{situation}\"\"\"

Respond with a single JSON object matching this shape exactly:

{JSON_EXAMPLE}

Rules:
- `severity` MUST be one of: NOT_COOKED, SLIGHTLY_COOKED, GETTING_WARM, MEDIUM_RARE, HEAVILY_COOKED, DEEPLY_COOKED, BEYOND_REPAIR
- `category` MUST be one of: academic, career, relationship, money, life, technology, social, time, chaos, other
- `recovery_plan`: 4-6 items, practical and ordered.
- `emergency_actions`: 3-5 items, only if score >= 71, otherwise an empty list.
- `what_happens_next`: 3-5 items with `when` (e.g. "In 10 minutes") and `what`.
- `confidence`: float 0.0-1.0.
- Return ONLY the JSON object. No markdown fences, no commentary, no apologies.
"""