"""
Deterministic demo provider. Produces realistic, reactive responses with
zero API keys.

Design goals:
- Same input → same output (deterministic per situation string).
- Different inputs → different diagnoses, plans, and next-steps.
- Content reflects WHAT the user actually said, not a fixed template.
"""
from __future__ import annotations

from typing import Any, Dict, List

from .base import AIProvider
from ...utils.signals import Signals, extract_signals, pick
from ...utils.scoring import severity_for_score


BASE_SCORE = 35  # neutral starting point


class MockProvider(AIProvider):
    name = "mock"

    async def analyze(self, situation: str, category: str) -> Dict[str, Any]:
        sig = extract_signals(situation)
        score = self._compute_score(sig)
        sev = severity_for_score(score)
        resolved_category = category if category != "auto" else sig.category
        if resolved_category not in self._known_categories():
            resolved_category = sig.category

        recovery = self._recovery_probability(score, sig)

        return {
            "score": score,
            "severity": sev,
            "category": resolved_category,
            "diagnosis": self._diagnosis(sig, score),
            "reasons": self._reasons(sig, resolved_category),
            "risk_factors": self._risk_factors(sig, resolved_category),
            "recovery_probability": recovery,
            "recovery_plan": self._recovery_plan(sig, resolved_category, score),
            "emergency_actions": self._emergency_actions(sig, resolved_category, score),
            "funny_commentary": self._commentary(sig, score),
            "what_happens_next": self._what_next(sig, score),
            "confidence": 0.72 if sig.matched_phrases else 0.4,
            "demo_mode": True,
        }

    async def what_next(self, situation: str, score: int) -> Dict[str, Any]:
        sig = extract_signals(situation)
        return {"items": self._what_next(sig, score)}

    # ------------------------------------------------------------------
    # Score
    # ------------------------------------------------------------------
    @staticmethod
    def _compute_score(sig: Signals) -> int:
        raw = BASE_SCORE + sig.score_delta
        # Slightly compress the extremes so we don't hit 3/99 too often
        if raw <= 5:
            raw = 5
        if raw >= 97:
            raw = 97
        return max(3, min(99, raw))

    @staticmethod
    def _recovery_probability(score: int, sig: Signals) -> int:
        # Higher score → lower recovery, but positive notes push it up
        base = 100 - score
        base += 5 * len(sig.positive_notes)
        base -= 3 * len(sig.risk_notes)
        return max(5, min(95, base))

    # ------------------------------------------------------------------
    # Diagnosis
    # ------------------------------------------------------------------
    def _diagnosis(self, sig: Signals, score: int) -> str:
        opener = self._opener(sig, score)
        middle = self._middle(sig, score)
        closer = self._closer(sig, score)
        parts = [p for p in (opener, middle, closer) if p]
        return " ".join(parts)[:400]

    def _opener(self, sig: Signals, score: int) -> str:
        cat = sig.category
        if score >= 90:
            by_cat = {
                "academic":     "You are approaching charred.",
                "career":       "This is a five-alarm career situation.",
                "relationship": "The oven has been set to cremate.",
                "money":        "You are functionally out of runway.",
                "technology":   "The system has collapsed in a way that feels personal.",
                "social":       "You have managed to escalate a text into an event.",
                "time":         "You are the wrong side of every clock in the room.",
                "other":        "You are not cooked. You are ash.",
            }
        elif score >= 75:
            by_cat = {
                "academic":     "The oven is preheated and it knows your name.",
                "career":       "You are one bad minute away from a really bad meeting.",
                "relationship": "There is still a window, and it is closing fast.",
                "money":        "The math is not on your side.",
                "technology":   "The setup is against you and it is winning.",
                "social":       "The message is out. Damage control starts now.",
                "time":         "You have less time than you think.",
                "other":        "You are properly cooked on the outside.",
            }
        elif score >= 50:
            by_cat = {
                "academic":     "There's still time, but the clock is filing a complaint.",
                "career":       "This is a warm situation. Not yet on fire.",
                "relationship": "You have room to fix this if you move soon.",
                "money":        "It's tight, not terminal.",
                "technology":   "This is fixable, but not with the tools you currently trust.",
                "social":       "Nothing has exploded. Yet.",
                "time":         "You are behind, but the race isn't over.",
                "other":        "You are medium rare and climbing.",
            }
        elif score >= 25:
            by_cat = {
                "academic":     "This is a speedbump, not a wall.",
                "career":       "There's more prep than panic here.",
                "relationship": "This is a text, not a divorce.",
                "money":        "It's tight, but there's a plan-shaped path.",
                "technology":   "Annoying, not catastrophic.",
                "social":       "Nobody will remember this in a week.",
                "time":         "You're on schedule. Slightly.",
                "other":        "You're warm, not cooking.",
            }
        else:
            by_cat = {
                "academic":     "Suspiciously well-prepared.",
                "career":       "You might actually be fine.",
                "relationship": "This is a normal day, not a crisis.",
                "money":        "You are not in trouble.",
                "technology":   "The laptop will survive.",
                "social":       "Nobody is upset.",
                "time":         "You have time to spare.",
                "other":        "You're not cooked. You're barely in the kitchen.",
            }
        return by_cat.get(cat, by_cat["other"])

    def _middle(self, sig: Signals, score: int) -> str:
        # Weave in the specific thing they said
        bits = []
        if sig.time_pressure:
            bits.append(f"Time pressure: {sig.time_pressure}.")
        if sig.prep_state:
            bits.append(f"Prep state: {sig.prep_state}.")
        if bits and score >= 40:
            return " ".join(bits)
        return ""

    def _closer(self, sig: Signals, score: int) -> str:
        easter = ""
        t = sig.raw.lower()
        if any(p in t for p in ("i'm fine", "im fine", "i am fine")):
            easter = "(That's exactly what someone who is cooked would say.)"
        if score >= 86 and not easter:
            return pick([
                "You are not medium rare anymore. You are charcoal.",
                "The oven has accepted you as one of its own.",
                "Somewhere a fire alarm is going off on your behalf.",
            ], sig.seed)
        if score >= 50 and not easter:
            return pick([
                "Fixable, if you start in the next ten minutes.",
                "You still have options. Fewer than yesterday, more than tomorrow.",
                "The clock is not your enemy yet. It will be.",
            ], sig.seed, 1)
        return easter

    # ------------------------------------------------------------------
    # Reasons
    # ------------------------------------------------------------------
    def _reasons(self, sig: Signals, category: str) -> List[Dict[str, str]]:
        reasons: List[Dict[str, str]] = []

        # Category-specific lead-in
        cat_reasons = {
            "academic":     ("📚", "Academic preparation is behind schedule"),
            "career":       ("💼", "Career stakes are elevated"),
            "relationship": ("❤️", "Interpersonal damage risk"),
            "money":        ("💰", "Financial runway is compressed"),
            "technology":   ("💻", "Technical setup is unstable"),
            "social":       ("🗣️", "Social consequences are in play"),
            "time":         ("⏰", "Timeline is not cooperating"),
            "other":        ("🎯", "Situation is under-specified"),
        }
        if category in cat_reasons:
            e, l = cat_reasons[category]
            reasons.append({"emoji": e, "label": l})

        # Signal-specific reasons
        if sig.time_pressure:
            reasons.append({"emoji": "⏰", "label": f"Time: {sig.time_pressure}"})
        if sig.prep_state:
            reasons.append({"emoji": "📉", "label": f"Preparation: {sig.prep_state}"})
        if any(r in ("final exam/stage", "career-defining", "life-changing")
               for r in sig.risk_notes):
            reasons.append({"emoji": "🚨", "label": "High-stakes context"})
        if "multiple parties involved" in sig.risk_notes:
            reasons.append({"emoji": "👥", "label": "Multiple people affected"})
        if not reasons:
            reasons.append({"emoji": "❓", "label": "Situation details are thin"})

        # Cap at 5, keep order
        return reasons[:5]

    # ------------------------------------------------------------------
    # Risk factors
    # ------------------------------------------------------------------
    def _risk_factors(self, sig: Signals, category: str) -> List[str]:
        risks = []
        if sig.time_pressure in ("minutes/hours away", "already late", "no time left"):
            risks.append("Little to no buffer time")
        if sig.prep_state in ("not started", "not touched"):
            risks.append("Starting from zero")
        if "broad stakes" in sig.risk_notes:
            risks.append("Ripple effects on multiple areas")
        if category == "money":
            risks.append("Runway shrinking daily")
        elif category == "academic":
            risks.append("Cognitive load peak coincides with deadline")
        elif category == "career":
            risks.append("First impression is already forming")
        elif category == "relationship":
            risks.append("Silence interpreted as guilt")
        elif category == "technology":
            risks.append("Compounding technical debt")

        # Fallback
        if not risks:
            risks.append("No obvious acute risk")
            risks.append("Situation may be under-reported")
        return risks[:4]

    # ------------------------------------------------------------------
    # Recovery plan
    # ------------------------------------------------------------------
    def _recovery_plan(self, sig: Signals, category: str, score: int) -> List[str]:
        # Shared opening
        if score >= 71:
            plan = [
                "Stop everything unrelated to the critical path.",
                "Pick ONE task that unblocks the rest. Write it down.",
            ]
        elif score >= 31:
            plan = [
                "Close the tabs you're not using.",
                "Pick the highest-leverage task. Start it in the next 5 minutes.",
            ]
        else:
            plan = [
                "You're in decent shape. Keep doing what you're doing.",
                "Confirm your plan is still valid.",
            ]

        # Category-specific middle steps
        if category == "academic":
            plan += [
                "Skim headings and past papers — not the entire textbook.",
                "Write a 5-line cheat sheet of the top concepts.",
                "Work 25 minutes. Short break. Repeat.",
            ]
        elif category == "career":
            plan += [
                "Re-read the job description / agenda and note 3 talking points.",
                "Prepare one thoughtful question to ask them.",
                "Run a 2-minute mock answer out loud for the first question.",
            ]
        elif category == "relationship":
            plan += [
                "Write the message you wish you'd sent. Don't send it yet.",
                "Wait 10 minutes. Reread it. Send the calmer version.",
                "If it escalates, ask to talk on a call instead of text.",
            ]
        elif category == "money":
            plan += [
                "List every recurring expense due before payday.",
                "Cut anything that isn't rent, food, or transport.",
                "If you need help, ask one person today.",
            ]
        elif category == "technology":
            plan += [
                "Isolate the failure — one variable at a time.",
                "Check logs before guessing.",
                "If stuck for 20 minutes, ask for help or read docs, not forums.",
            ]
        elif category == "social":
            plan += [
                "Own the mistake plainly. No joke, no deflection.",
                "Offer a specific fix, not a vague apology.",
                "Then stop. Don't over-explain.",
            ]
        else:
            plan += [
                "Break the goal into the smallest useful next action.",
                "Do that one thing. Then reassess.",
            ]

        # Score-tuned closer
        if score >= 86:
            plan.append("Sleep tonight. All-nighters make tomorrow worse.")
        elif score >= 50:
            plan.append("Reassess in 2 hours — the number should be dropping.")
        else:
            plan.append("You're fine. Take a real break when this is done.")

        return plan[:6]

    # ------------------------------------------------------------------
    # Emergency actions
    # ------------------------------------------------------------------
    def _emergency_actions(self, sig: Signals, category: str, score: int) -> List[str]:
        if score < 71:
            return []

        if category == "academic":
            return [
                "Phone in another room. Timer on the desk.",
                "Work only on the highest-weight topic.",
                "Skip everything you already know.",
                "Set a 25-minute timer and do not stop until it rings.",
                "After the timer: 3 minutes of movement, then repeat.",
            ]
        if category == "career":
            return [
                "Prepare the 3 questions you'll ask them.",
                "Write the first 60 seconds of your answer out loud.",
                "Close every tab that isn't the job description.",
                "Leave 10 minutes early so you're not rushing.",
            ]
        if category == "relationship":
            return [
                "Do not send anything else until you've waited 10 minutes.",
                "Write it in notes first. Read it aloud.",
                "Choose the version you'd be okay reading back in a year.",
            ]
        if category == "money":
            return [
                "List the next 5 payments in order.",
                "Call anyone you owe before they call you.",
                "Pause all non-essential subscriptions today.",
            ]
        if category == "technology":
            return [
                "Stop changing multiple things at once.",
                "Roll back to the last known-good state.",
                "Read the actual error message.",
                "Ask for help after 20 minutes, not 2 hours.",
            ]
        return [
            "Close all non-essential tabs and apps.",
            "Put your phone in another room.",
            "Set a 25-minute timer.",
            "Work on the ONE thing that matters most.",
        ]

    # ------------------------------------------------------------------
    # Funny commentary
    # ------------------------------------------------------------------
    def _commentary(self, sig: Signals, score: int) -> str:
        if score >= 96:
            return "Congratulations. You have achieved maximum cook."
        if score >= 86:
            return pick([
                "Bro is not medium rare anymore. Bro is charcoal.",
                "The fire department has been notified.",
                "You are legally a brisket now.",
                "Somewhere, a smoke alarm just went off.",
            ], sig.seed)
        if score >= 71:
            return pick([
                "The oven is preheated. The chicken has accepted its fate.",
                "The heat is on and it is personal.",
                "The situation is warm and getting warmer.",
            ], sig.seed, 1)
        if score >= 51:
            return pick([
                "The oven is warm. The chicken is nervous.",
                "You're cooking, not burnt. Yet.",
                "There's a nice char forming on the edges.",
            ], sig.seed, 2)
        if score >= 31:
            return pick([
                "You might actually survive this. Don't get cocky.",
                "You're simmering. Not boiling.",
                "The chicken is still clucking. That's a good sign.",
            ], sig.seed, 3)
        return pick([
            "You might actually survive this. Suspicious.",
            "The oven isn't even on. Show-off.",
            "You are basically room temperature.",
        ], sig.seed, 4)

    # ------------------------------------------------------------------
    # What happens next
    # ------------------------------------------------------------------
    def _what_next(self, sig: Signals, score: int) -> List[Dict[str, str]]:
        # Use matched signals to make the predictions feel specific
        cat = sig.category

        if score >= 86:
            return [
                {"when": "In 5 minutes",  "what": "You will refresh a page you don't need to refresh."},
                {"when": "In 20 minutes", "what": self._next_impulse(cat)},
                {"when": "In 2 hours",    "what": "You will suddenly remember you have a body and it needs water."},
                {"when": "Tonight",       "what": "You will either fix one thing or fall asleep trying."},
                {"when": "Tomorrow",      "what": "You will promise yourself this will never happen again."},
            ]
        if score >= 51:
            return [
                {"when": "In 15 minutes", "what": "You will start, slowly."},
                {"when": "In 1 hour",     "what": "You will be surprised by your own progress."},
                {"when": "Tonight",       "what": "You will wonder why you panicked."},
            ]
        if score >= 31:
            return [
                {"when": "In 30 minutes", "what": "You will finish ahead of schedule."},
                {"when": "Later today",   "what": "You will take an unearned victory lap."},
            ]
        return [
            {"when": "In 1 hour", "what": "You will forget this app exists."},
            {"when": "Tomorrow",  "what": "You will tell everyone you 'wasn't even stressed'."},
        ]

    @staticmethod
    def _next_impulse(category: str) -> str:
        if category == "academic":
            return "You will open YouTube 'for background music'."
        if category == "career":
            return "You will reread the same sentence in the job description three times."
        if category == "relationship":
            return "You will draft a message and delete it three times."
        if category == "money":
            return "You will redo the same math hoping it changes."
        if category == "technology":
            return "You will close and reopen the terminal, hoping."
        return "You will open one more tab 'just to check'."

    @staticmethod
    def _known_categories() -> set:
        return {
            "academic", "career", "relationship", "money", "life",
            "technology", "social", "time", "chaos", "other",
        }