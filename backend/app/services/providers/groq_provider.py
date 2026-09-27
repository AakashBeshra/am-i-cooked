"""
Groq provider — narrative-only mode.

The rules engine has already:
  1. Parsed the situation into a Scene
  2. Computed a deterministic score

This provider asks Groq to fill in ONLY the human-readable narrative fields:
diagnosis, reasons, risk_factors, recovery_plan, emergency_actions,
funny_commentary, what_happens_next.

Score is NOT sent to Groq, and Groq's score is ignored — this is what
keeps the Cooked Score deterministic and prevents token-burn on scoring.
"""
from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict

import httpx

from .base import AIProvider, ProviderError

logger = logging.getLogger("am_i_cooked.groq")


NARRATIVE_SYSTEM = """You are the analyst voice of "AM I COOKED?" — a witty \
but caring app that scores how badly someone has messed up a situation.

You will receive:
- A structured Scene: parsed facts about WHO is involved, WHAT happened or \
is happening, WHEN the deadline is, HOW serious it is, and what has already \
gone wrong.
- A deterministic COOKED SCORE (0-100) that YOU MUST NOT CHANGE OR QUESTION.
- The user's raw situation text for context.

Your job: write the narrative fields. Nothing else.

RULES:
- Do NOT output a score. Do NOT re-judge the score. Accept it.
- Diagnosis: 1-2 sentences. Funny but useful. Reference specific facts.
- Reasons: 3-5 items. Each has an emoji and a short label (max 12 words).
- Risk factors: 3-4 items. Plain text, no emoji, max 10 words each.
- Recovery plan: 4-6 concrete, ordered steps. Address the actual situation.
- Emergency actions: 4-5 items if score >= 70, else an empty array.
- Funny commentary: one punchline. Internet tone. Not mean.
- What happens next: 3-5 fictional predictions with "when" and "what".
- Be honest. Do not inflate humor to hide useful advice.

OUTPUT FORMAT:
- Respond with ONLY a raw JSON object. No markdown fences. No reasoning \
tags. No thinking blocks. No preamble. No trailing commentary.
- Start your response with the character { and end with the character }.
- If you catch yourself writing anything before {, delete it and start over.
"""


NARRATIVE_SCHEMA_HINT = {
    "diagnosis": "One or two sentences naming the specific situation.",
    "reasons": [{"emoji": "⏰", "label": "Short label"}],
    "risk_factors": ["Short risk", "Another risk"],
    "recovery_plan": ["Step 1", "Step 2", "Step 3"],
    "emergency_actions": ["Action 1", "Action 2"],
    "funny_commentary": "One punchline.",
    "what_happens_next": [
        {"when": "In 10 minutes", "what": "You will do X."},
    ],
}


class GroqProvider(AIProvider):
    name = "groq"

    def __init__(self, api_key: str, model: str, base_url: str, timeout: float = 25.0) -> None:
        if not api_key:
            raise ProviderError("Groq API key not configured.")
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._client: httpx.AsyncClient | None = None

    async def _client_instance(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client

    async def aclose(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def analyze(self, situation: str, category: str) -> Dict[str, Any]:
        # Groq no longer analyzes full situations — the AIService handles
        # parsing and scoring. This method exists only to satisfy the ABC,
        # and is never called by AIService.
        raise ProviderError(
            "GroqProvider.analyze is not used. Call .narrate() with a Scene."
        )

    async def narrate(
        self,
        situation: str,
        scene_dict: Dict[str, Any],
        score: int,
        severity: str,
        category: str,
    ) -> Dict[str, Any]:
        """Produce the narrative fields only. Returns a dict matching
        the shape of narrative.rules_narrate() minus score/severity/category."""
        client = await self._client_instance()

        user_prompt = self._build_user_prompt(
            situation=situation,
            scene_dict=scene_dict,
            score=score,
            severity=severity,
            category=category,
        )

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": NARRATIVE_SYSTEM},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.6,
            "max_tokens": 1200,
            # NOTE: We intentionally do NOT set response_format=json_object.
            # gpt-oss-* models on Groq reject that mode with HTTP 400
            # (json_validate_failed / empty generation). Instead we rely on
            # the system prompt to enforce JSON and strip any fences here.
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            r = await client.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=headers,
            )
            r.raise_for_status()
            data = r.json()
            raw = data["choices"][0]["message"]["content"] or ""
        except httpx.HTTPStatusError as e:
            # Extract just the message from Groq's error JSON when possible
            detail = e.response.text[:300]
            try:
                err = e.response.json()
                detail = err.get("error", {}).get("message", detail)
            except Exception:
                pass
            raise ProviderError(f"Groq HTTP {e.response.status_code}: {detail}") from e
        except (httpx.HTTPError, KeyError, IndexError) as e:
            raise ProviderError(f"Groq transport error: {e}") from e

        cleaned = self._extract_json(raw)
        if not cleaned:
            raise ProviderError(
                f"Groq returned no JSON. Raw length={len(raw)}. "
                f"First 200 chars: {raw[:200]!r}"
            )

        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError as e:
            raise ProviderError(
                f"Groq returned invalid JSON: {e}. Raw: {cleaned[:200]!r}"
            ) from e

        return self._normalize(parsed)

    async def what_next(self, situation: str, score: int) -> Dict[str, Any]:
        # Handled inside narrate(). Not called separately.
        raise ProviderError("GroqProvider.what_next is not used in narrative mode.")

    # ------------------------------------------------------------------
    # Prompt building
    # ------------------------------------------------------------------

    @staticmethod
    def _build_user_prompt(
        situation: str,
        scene_dict: Dict[str, Any],
        score: int,
        severity: str,
        category: str,
    ) -> str:
        # Trim scene to essentials to keep token count low
        scene_trimmed = {
            k: v for k, v in scene_dict.items()
            if k in (
                "actors", "primary_event", "hours_remaining", "deadline_phrase",
                "domain", "stakes", "consequence_type", "consequence_severity",
                "reversibility", "user_prepared",
            )
        }
        schema_example = json.dumps(NARRATIVE_SCHEMA_HINT, ensure_ascii=False, indent=2)

        return f"""USER'S RAW SITUATION:
\"\"\"{situation}\"\"\"

PARSED SCENE (facts extracted by the rules engine):
{json.dumps(scene_trimmed, ensure_ascii=False, indent=2)}

DETERMINISTIC SCORE (do not change, do not re-judge):
{score} / 100  →  severity: {severity}  →  category: {category}

Respond with a single JSON object matching this shape EXACTLY:

{schema_example}

Constraints:
- reasons: 3-5 items, each emoji is a single emoji, label is <= 12 words.
- risk_factors: 3-4 items, plain text, <= 10 words each.
- recovery_plan: 4-6 items, concrete and situation-aware.
- emergency_actions: 4-5 items IF score >= 70, else empty array [].
- funny_commentary: one punchline, internet voice, not mean.
- what_happens_next: 3-5 items with "when" (e.g. "In 10 minutes") and "what".

Respond with ONLY the JSON object. No markdown, no code fences, no commentary."""

    # ------------------------------------------------------------------
    # Response parsing
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_json(text: str) -> str:
        """
        Robustly extract a JSON object from a model response.

        Handles:
        - Plain JSON:  {"score": 96, ...}
        - Fenced:      ```json\\n{...}\\n```
        - Preamble:    "Here is the JSON: {...}"
        - Reasoning:   "<thinking>...</thinking>\\n{...}"  (gpt-oss style)
        - Trailing:    "{...}\\n\\nHope this helps!"
        """
        if not text:
            return ""

        s = text.strip()

        # Strip reasoning tags common in gpt-oss output
        s = re.sub(r"<\|.*?\|>", "", s, flags=re.DOTALL)
        s = re.sub(r"</?think(ing)?>", "", s, flags=re.IGNORECASE)
        s = re.sub(r"</?reasoning>", "", s, flags=re.IGNORECASE)

        # Strip markdown code fences
        if s.startswith("```"):
            s = re.sub(r"^```[a-zA-Z]*\s*", "", s)
            s = re.sub(r"\s*```\s*$", "", s)

        s = s.strip()

        # If it starts with "{", find the matching closing brace.
        if s.startswith("{"):
            depth = 0
            in_string = False
            escape = False
            for i, ch in enumerate(s):
                if escape:
                    escape = False
                    continue
                if ch == "\\":
                    escape = True
                    continue
                if ch == '"':
                    in_string = not in_string
                    continue
                if in_string:
                    continue
                if ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                    if depth == 0:
                        return s[: i + 1]

        # Fallback: find the first { ... } block anywhere
        start = s.find("{")
        end = s.rfind("}")
        if start != -1 and end != -1 and end > start:
            return s[start : end + 1]

        return ""

    @staticmethod
    def _normalize(raw: Dict[str, Any]) -> Dict[str, Any]:
        """Coerce Groq's output into the shape the rest of the app expects."""
        # reasons
        reasons = []
        for item in (raw.get("reasons") or [])[:6]:
            if isinstance(item, dict) and item.get("label"):
                reasons.append({
                    "emoji": str(item.get("emoji", "•"))[:4],
                    "label": str(item.get("label"))[:120],
                })
            elif isinstance(item, str) and item.strip():
                reasons.append({"emoji": "•", "label": item[:120]})

        # risk factors
        risks = [
            str(x)[:120] for x in (raw.get("risk_factors") or [])[:6]
            if isinstance(x, (str, int, float))
        ]

        # recovery plan
        plan = [
            str(x)[:200] for x in (raw.get("recovery_plan") or [])[:8]
            if isinstance(x, (str, int, float))
        ]

        # emergency actions
        emergency = [
            str(x)[:150] for x in (raw.get("emergency_actions") or [])[:8]
            if isinstance(x, (str, int, float))
        ]

        # what happens next
        what_next = []
        for item in (raw.get("what_happens_next") or [])[:6]:
            if isinstance(item, dict) and item.get("when") and item.get("what"):
                what_next.append({
                    "when": str(item["when"])[:60],
                    "what": str(item["what"])[:200],
                })

        return {
            "diagnosis": str(raw.get("diagnosis") or "")[:400],
            "reasons": reasons,
            "risk_factors": risks,
            "recovery_plan": plan,
            "emergency_actions": emergency,
            "funny_commentary": str(raw.get("funny_commentary") or "")[:300],
            "what_happens_next": what_next,
        }