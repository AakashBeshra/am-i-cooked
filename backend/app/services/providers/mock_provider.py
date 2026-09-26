"""
Deterministic demo provider. Produces realistic, useful responses with
zero API keys. The rest of the app doesn't care that it's fake — this
is what makes the whole project runnable out of the box.
"""
from __future__ import annotations

import random
from typing import Any, Dict, List

from .base import AIProvider
from ...utils.scoring import heuristic_score, severity_for_score


# Category guessing — cheap keyword classifier, good enough for demo mode.
CATEGORY_KEYWORDS = {
    "academic": ["exam", "test", "study", "assignment", "homework", "professor",
                 "class", "course", "grade", "school", "college", "university",
                 "project", "semester", "thesis", "quiz", "syllabus"],
    "career": ["boss", "interview", "job", "resume", "cv", "promotion", "office",
               "meeting", "client", "offer", "manager", "colleague", "salary",
               "internship", "hr"],
    "relationship": ["girlfriend", "boyfriend", "wife", "husband", "partner",
                     "date", "crush", "ex", "breakup", "texted", "cheated",
                     "relationship", "anniversary", "valentine"],
    "money": ["money", "cash", "₹", "$", "€", "broke", "payday", "salary",
              "rent", "bill", "loan", "debt", "budget", "broke", "expensive"],
    "technology": ["code", "python", "java", "javascript", "react", "api", "server",
                   "database", "bug", "deploy", "laptop", "windows", "update",
                   "computer", "software", "compile", "github"],
    "social": ["texted", "message", "group chat", "whatsapp", "instagram", "tweet",
               "posted", "comment", "reply", "story", "dm"],
    "time": ["late", "deadline", "tomorrow", "tonight", "minutes", "hours",
             "schedule", "calendar", "appointment"],
}


def guess_category(text: str) -> str:
    t = text.lower()
    best_cat = "other"
    best_hits = 0
    for cat, keywords in CATEGORY_KEYWORDS.items():
        hits = sum(1 for kw in keywords if kw in t)
        if hits > best_hits:
            best_hits = hits
            best_cat = cat
    if best_hits == 0 and "chaos" in t:
        return "chaos"
    return best_cat


REASON_BANK: Dict[str, List[Dict[str, str]]] = {
    "academic": [
        {"emoji": "⏰", "label": "Very little time before the deadline"},
        {"emoji": "📚", "label": "Very low preparation for the material"},
        {"emoji": "🧠", "label": "Cognitive overload risk is high"},
        {"emoji": "📱", "label": "Severe distraction risk during study"},
    ],
    "career": [
        {"emoji": "⏰", "label": "Very little time before the meeting"},
        {"emoji": "📄", "label": "Preparation level is low"},
        {"emoji": "😰", "label": "Elevated stakes reduce performance"},
        {"emoji": "🎯", "label": "Unclear priorities going in"},
    ],
    "relationship": [
        {"emoji": "💬", "label": "Communication has already happened"},
        {"emoji": "⏳", "label": "Damage control window is short"},
        {"emoji": "😬", "label": "Interpretation risk is high"},
        {"emoji": "📱", "label": "Screenshots may exist"},
    ],
    "money": [
        {"emoji": "💸", "label": "Runway is shorter than the pay cycle"},
        {"emoji": "📉", "label": "No buffer for emergencies"},
        {"emoji": "🛒", "label": "Essential spending will eat the remainder"},
        {"emoji": "😰", "label": "Financial stress compounds decisions"},
    ],
    "technology": [
        {"emoji": "🐛", "label": "Unexpected technical failure"},
        {"emoji": "⏰", "label": "Very little time to recover"},
        {"emoji": "💻", "label": "Environment may not cooperate"},
        {"emoji": "📉", "label": "Debugging has diminishing returns"},
    ],
    "time": [
        {"emoji": "⏰", "label": "Very little time remaining"},
        {"emoji": "🗓️", "label": "Schedule is overcommitted"},
        {"emoji": "😭", "label": "Elevated panic signature detected"},
        {"emoji": "📱", "label": "Context-switching cost is high"},
    ],
    "other": [
        {"emoji": "⏰", "label": "Very little time remaining"},
        {"emoji": "📚", "label": "Low preparation detected"},
        {"emoji": "😭", "label": "Elevated panic signature"},
        {"emoji": "📱", "label": "Severe distraction risk"},
    ],
}


class MockProvider(AIProvider):
    name = "mock"

    async def analyze(self, situation: str, category: str) -> Dict[str, Any]:
        score = heuristic_score(situation)
        sev = severity_for_score(score)
        category = category if category != "auto" else guess_category(situation)
        if category not in REASON_BANK:
            category = "other"

        recovery = max(5, min(95, 100 - score + 20))

        diagnosis = self._diagnosis_for(score, situation)
        commentary = self._commentary_for(score)
        reasons = REASON_BANK[category]
        risks = self._risks_for(category)
        plan = self._recovery_plan_for(score, category)
        emergency = self._emergency_for(score)

        return {
            "score": score,
            "severity": sev,
            "category": category,
            "diagnosis": diagnosis,
            "reasons": reasons,
            "risk_factors": risks,
            "recovery_probability": recovery,
            "recovery_plan": plan,
            "emergency_actions": emergency,
            "funny_commentary": commentary,
            "what_happens_next": self._what_next(situation, score),
            "confidence": 0.72,
            "demo_mode": True,
        }

    async def what_next(self, situation: str, score: int) -> Dict[str, Any]:
        return {"items": self._what_next(situation, score)}

    # ---------- content helpers ----------

    @staticmethod
    def _diagnosis_for(score: int, situation: str) -> str:
        t = situation.lower()
        easter = ""
        if "i'm fine" in t or "im fine" in t or "i am fine" in t:
            easter = " (That's exactly what someone who is cooked would say.)"
        if score >= 96:
            return "You are statistically indistinguishable from charcoal." + easter
        if score >= 86:
            return "You're not completely doomed, but the oven is definitely preheating." + easter
        if score >= 71:
            return "There's still time — but not enough to keep pretending." + easter
        if score >= 51:
            return "The chicken is nervous. The clock is filing a complaint." + easter
        if score >= 31:
            return "You're warming up, but the fire isn't lit yet." + easter
        if score >= 11:
            return "Slightly toasted. Honestly, manageable." + easter
        return "Suspiciously responsible behavior detected." + easter

    @staticmethod
    def _commentary_for(score: int) -> str:
        if score >= 96:
            return "Congratulations. You have achieved maximum cook."
        if score >= 86:
            return "Bro is not medium rare anymore. Bro is charcoal."
        if score >= 71:
            return "The oven is preheated. The chicken has accepted its fate."
        if score >= 51:
            return "The oven is warm. The chicken is nervous."
        if score >= 31:
            return "You might actually survive this. Don't get cocky."
        return "You might actually survive this. Suspicious."

    @staticmethod
    def _risks_for(category: str) -> List[str]:
        by_cat = {
            "academic": ["Procrastination compounding", "Diminishing returns on cramming", "Sleep debt affecting recall"],
            "career":   ["Preparation ceiling", "Nervousness reducing clarity", "Unclear success criteria"],
            "relationship": ["Damage to trust", "Escalation risk if unaddressed", "Worsening with silence"],
            "money":    ["Runway shrinking daily", "Emergency spending risk", "Compounding stress"],
            "technology": ["Environment instability", "Rollback complexity", "Time lost to recovery"],
            "time":     ["Schedule overcommitment", "Context-switching overhead", "Rising panic cost"],
            "other":    ["Procrastination compounding", "Context-switching overhead", "Diminishing returns on effort"],
        }
        return by_cat.get(category, by_cat["other"])

    @staticmethod
    def _recovery_plan_for(score: int, category: str) -> List[str]:
        base = [
            "Stop scrolling. Right now.",
            "Identify the single highest-priority task.",
            "Work 60–90 minutes without interruption.",
            "Short break. Water. Repeat.",
            "Do not attempt to solve everything simultaneously.",
        ]
        if score >= 86:
            return [
                "Emergency triage: pick ONE task that unblocks everything else.",
                "Close every tab, app, and chat that isn't that task.",
                "Set a 25-minute timer. Work until it rings. No exceptions.",
                "Drink water. Two minutes of walking. Back to work.",
                "Assess: is the crisis smaller now? Repeat the cycle.",
                "Sleep. Seriously. All-nighters are a bad trade at this stage.",
            ]
        if score >= 51:
            return base + ["Reassess in 2 hours — the number should be dropping."]
        if score >= 11:
            return [
                "Skim the goal. Define 'done'.",
                "Block 45 minutes. Work on the highest-leverage part.",
                "Take a 10-minute break. Come back.",
                "You're fine. Stay consistent.",
            ]
        return ["Keep doing whatever you're doing. It's working.", "Take a victory lap. Just one."]

    @staticmethod
    def _emergency_for(score: int) -> List[str]:
        if score < 71:
            return []
        return [
            "Close all non-essential tabs and apps.",
            "Put your phone in another room.",
            "Set a 25-minute timer.",
            "Work on the ONE thing that matters most.",
            "If the timer rings and you're in flow, extend by 10 minutes.",
        ]

    @staticmethod
    def _what_next(situation: str, score: int) -> List[Dict[str, str]]:
        if score >= 86:
            return [
                {"when": "In 10 minutes", "what": "You will open YouTube 'just to check one thing'."},
                {"when": "In 25 minutes", "what": "You will convince yourself one episode won't hurt."},
                {"when": "In 2 hours",   "what": "You will suddenly discover motivation."},
                {"when": "Tomorrow",     "what": "You will promise yourself this will never happen again."},
            ]
        if score >= 51:
            return [
                {"when": "In 15 minutes", "what": "You will start. Slowly."},
                {"when": "In 1 hour",     "what": "You will be surprised by your own progress."},
                {"when": "Tomorrow",      "what": "You will wonder why you panicked."},
            ]
        return [
            {"when": "In 30 minutes", "what": "You will finish early and feel smug."},
            {"when": "Tomorrow",      "what": "You will tell everyone you 'wasn't even stressed'."},
        ]