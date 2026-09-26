"""
Structured situation analysis.

Instead of flat match-and-add scoring, we extract a Scene describing:
- WHO is involved
- WHAT kind of event this is (pending / completed / ongoing / feeling)
- WHEN the deadline is (parsed to hours remaining)
- HOW MUCH is at stake
- HOW MUCH control the user has
- WHAT has already happened (consequences)

The Scene then drives BOTH scoring and narrative generation.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from typing import List, Optional


# -----------------------------------------------------------------------------
# Vocabularies
# -----------------------------------------------------------------------------

ACTOR_WORDS = {
    "boss":      ["boss", "manager", "supervisor", "team lead", "lead"],
    "professor": ["professor", "teacher", "lecturer", "instructor", "principal",
                  "headmaster", "dean", "faculty"],
    "family":    ["mom", "dad", "mother", "father", "parents", "brother",
                  "sister", "sibling", "family"],
    "partner":   ["girlfriend", "boyfriend", "wife", "husband", "partner",
                  "fiance", "fiancee", "fiancé", "fiancée"],
    "peer":      ["friend", "friends", "roommate", "colleague", "classmate"],
    "authority": ["police", "officer", "cop", "judge", "court", "hr"],
    "client":    ["client", "customer", "stakeholder"],
}

EVENT_WORDS = {
    "exam":         ["exam", "test", "quiz", "midterm", "final", "paper"],
    "assignment":   ["assignment", "homework", "essay", "thesis", "dissertation",
                     "project", "report", "submission"],
    "interview":    ["interview", "screening", "call with hr"],
    "presentation": ["presentation", "demo", "pitch", "talk", "defense"],
    "deadline":     ["deadline", "due date", "due tomorrow", "due tonight"],
    "meeting":      ["meeting", "standup", "sync", "1:1"],
    "conflict":     ["fight", "argument", "argued", "yelled", "shouted",
                     "insulted", "slapped", "hit", "punched", "cursed", "swore",
                     "told off", "told to shut up"],
    "mistake":      ["texted", "sent to wrong", "posted", "uploaded", "replied",
                     "leaked", "accidentally", "by mistake", "oops"],
    "fired":        ["fired", "terminated", "let go", "laid off"],
    "breakup":      ["breakup", "broke up", "dumped", "ghosted"],
    "arrest":       ["arrested", "charged", "summons", "fir", "complaint filed"],
    "money_crisis": ["broke", "no money", "out of money", "lost all",
                     "scammed", "gambled", "spent everything",
                     "only have", "left and payday"],
    "health":       ["hospital", "overdose", "passed out", "fainted",
                     "fractured", "broke my"],
    "feeling":      ["overthinking", "worried", "nervous", "anxious", "stressed",
                     "scared", "tired", "burnt out", "exhausted"],
    "incomplete":   ["haven't started", "haven't studied", "haven't read",
                     "didn't study", "didn't prepare", "not started",
                     "nothing yet"],
}

DOMAIN_WORDS = {
    "academic":     ["exam", "test", "quiz", "study", "assignment", "homework",
                     "professor", "teacher", "class", "course", "grade",
                     "semester", "syllabus", "thesis", "university", "college",
                     "principal", "headmaster", "dean", "faculty", "school"],
    "career":       ["boss", "job", "interview", "career", "promotion", "resume",
                     "cv", "offer", "hr", "meeting", "presentation", "client",
                     "manager", "colleague", "standup", "work"],
    "relationship": ["girlfriend", "boyfriend", "wife", "husband", "partner",
                     "crush", "ex", "breakup", "anniversary", "date", "valentine",
                     "dating"],
    "money":        ["money", "cash", "broke", "payday", "salary", "rent",
                     "bill", "loan", "debt", "budget", "rupees", "dollars",
                     "euros", "pounds", "rupee", "dollar", "euro", "pound"],
    "technology":   ["code", "python", "java", "javascript", "react", "api",
                     "server", "database", "bug", "deploy", "laptop", "windows",
                     "update", "computer", "software", "compile", "github",
                     "charger", "battery", "phone"],
    "social":       ["texted", "message", "whatsapp", "instagram", "tweet",
                     "posted", "comment", "reply", "story", "dm", "screenshot",
                     "group chat"],
    "legal":        ["police", "arrested", "charged", "fir", "lawsuit", "court",
                     "summons", "judge"],
    "health":       ["hospital", "doctor", "sick", "injury", "pain", "fever",
                     "overdose", "fainted"],
}

# Consequence — how bad is what already happened? weight in [0, 1].
CONSEQUENCE_TYPES = {
    "physical_violence": (0.98, ["slapped", "hit", "punched", "pushed",
                                 "shoved", "kicked", "attacked", "assaulted"]),
    "legal":             (0.95, ["arrested", "charged", "fir", "lawsuit",
                                 "court", "summons", "police report"]),
    "disciplined":       (0.90, ["expelled", "suspended", "terminated",
                                 "fired", "let go"]),
    "academic_fraud":    (0.85, ["cheated", "plagiarized", "caught copying"]),
    "trust_breach":      (0.80, ["betrayed", "cheated on", "lied to everyone"]),
    "financial_ruin":    (0.85, ["lost all my money", "scammed", "gambled away",
                                 "spent everything"]),
    "health_emergency":  (0.90, ["overdose", "hospitalized", "passed out",
                                 "fractured", "broke my"]),
    "reputation_damage": (0.70, ["posted", "leaked", "screenshot", "went viral",
                                 "embarrassed myself"]),
    "mistake_sent":      (0.60, ["accidentally sent", "accidentally texted",
                                 "sent to wrong", "by mistake"]),
    "verbal_conflict":   (0.70, ["yelled at", "shouted at", "insulted",
                                 "cursed at", "swore at", "told off",
                                 "told to shut up"]),
}

# Time patterns — extract hours remaining. First match wins (smallest).
TIME_PATTERNS = [
    (r"\bin (\d+)\s*min(ute)?s?\b",     lambda m: int(m.group(1)) / 60),
    (r"\bin (\d+)\s*(hour|hr)s?\b",     lambda m: float(m.group(1))),
    (r"\bin (\d+)\s*days?\b",           lambda m: float(m.group(1)) * 24),
    (r"\bin (\d+)\s*weeks?\b",          lambda m: float(m.group(1)) * 168),
    (r"\btomorrow\b",                   lambda m: 18.0),
    (r"\btonight\b",                    lambda m: 8.0),
    (r"\btoday\b",                      lambda m: 6.0),
    (r"\bnext (monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b",
                                        lambda m: 120.0),
    (r"\bnext week\b",                  lambda m: 168.0),
    (r"\bnext month\b",                 lambda m: 720.0),
    (r"\balready late\b|\bi'?m late\b|\brunning late\b", lambda m: 0.0),
]

PREP_NEGATIVE = [
    r"\bhaven'?t (started|studied|prepared|read|opened|touched|begun|revised)\b",
    r"\b(didn'?t|don'?t) (study|prepare|start|read|revise)\b",
    r"\bnot started\b", r"\bnothing yet\b", r"\bi'?m behind\b",
]

PREP_POSITIVE = [
    r"\bi (have |had |'ve )?(already )?(prepared|studied|read|started|finished|revised)\b",
    r"\bi'?m ready\b", r"\ball set\b", r"\bi am ready\b",
    r"\bhalfway\b", r"\bmostly done\b", r"\balmost done\b",
]


# -----------------------------------------------------------------------------
# Data class
# -----------------------------------------------------------------------------

@dataclass
class Scene:
    raw: str
    seed: int = 0

    actors: List[str] = field(default_factory=list)
    events: List[str] = field(default_factory=list)
    primary_event: Optional[str] = None

    hours_remaining: Optional[float] = None
    deadline_phrase: Optional[str] = None

    domain: str = "other"
    secondary_domains: List[str] = field(default_factory=list)

    stakes: float = 0.5
    consequence_type: Optional[str] = None
    consequence_severity: float = 0.0
    reversibility: float = 1.0

    user_prepared: bool = False
    user_control: float = 0.5

    detected_phrases: List[str] = field(default_factory=list)


# -----------------------------------------------------------------------------
# Parser
# -----------------------------------------------------------------------------

def parse_scene(situation: str) -> Scene:
    text = (situation or "").strip()
    lower = text.lower()
    scene = Scene(raw=text, seed=_seed_from(text))

    # --- Actors ---
    for actor, words in ACTOR_WORDS.items():
        if any(re.search(rf"\b{re.escape(w)}\b", lower) for w in words):
            scene.actors.append(actor)

    # --- Events ---
    for event, words in EVENT_WORDS.items():
        for w in words:
            if w in lower:
                if event not in scene.events:
                    scene.events.append(event)
                scene.detected_phrases.append(w)

    # --- Primary event ---
    priority = [
        "arrest", "fired", "conflict", "money_crisis", "health",
        "breakup", "mistake", "incomplete",
        "exam", "interview", "presentation", "deadline", "assignment",
        "meeting", "feeling",
    ]
    for e in priority:
        if e in scene.events:
            scene.primary_event = e
            break

    # --- Timeline ---
    best_hours = None
    best_phrase = None
    for pattern, extractor in TIME_PATTERNS:
        m = re.search(pattern, lower)
        if m:
            hours = extractor(m)
            if best_hours is None or hours < best_hours:
                best_hours = hours
                best_phrase = m.group(0).strip()
    scene.hours_remaining = best_hours
    scene.deadline_phrase = best_phrase

    # --- Domains ---
    domain_hits = {}
    for dom, words in DOMAIN_WORDS.items():
        hits = sum(1 for w in words if re.search(rf"\b{re.escape(w)}\b", lower))
        if hits:
            domain_hits[dom] = hits
    if domain_hits:
        sorted_doms = sorted(domain_hits.items(), key=lambda x: -x[1])
        scene.domain = sorted_doms[0][0]
        scene.secondary_domains = [d for d, _ in sorted_doms[1:]]

    # --- Consequence ---
    for ctype, (weight, words) in CONSEQUENCE_TYPES.items():
        for w in words:
            if w in lower:
                if weight > scene.consequence_severity:
                    scene.consequence_severity = weight
                    scene.consequence_type = ctype
                scene.detected_phrases.append(w)

    # --- Stakes ---
    scene.stakes = _compute_stakes(scene, lower)

    # --- Reversibility ---
    if scene.consequence_severity > 0:
        scene.reversibility = 1.0 - scene.consequence_severity * 0.8
    elif scene.primary_event in ("fired", "arrest", "breakup"):
        scene.reversibility = 0.15

    # --- Preparedness ---
    if any(re.search(p, lower) for p in PREP_NEGATIVE):
        scene.user_prepared = False
    elif any(re.search(p, lower) for p in PREP_POSITIVE):
        scene.user_prepared = True
    else:
        # Default to False only if there's a pending event and no positive signal
        scene.user_prepared = False

    # --- Control ---
    control = 0.7
    if scene.consequence_severity > 0:
        control -= scene.consequence_severity * 0.5
    if "authority" in scene.actors or scene.domain == "legal":
        control -= 0.2
    if scene.primary_event in ("fired", "arrest", "breakup"):
        control -= 0.2
    if scene.primary_event in ("exam", "interview", "assignment", "deadline"):
        control += 0.15
    scene.user_control = max(0.05, min(0.95, control))

    return scene


def _compute_stakes(scene: Scene, lower: str) -> float:
    domain_stakes = {
        "academic":     0.55,
        "career":       0.65,
        "relationship": 0.60,
        "money":        0.70,
        "technology":   0.50,
        "social":       0.45,
        "legal":        0.90,
        "health":       0.85,
        "other":        0.40,
    }
    base = domain_stakes.get(scene.domain, 0.40)

    if re.search(r"\bfinal\b", lower):               base += 0.10
    if re.search(r"\bcareer[- ]?defining\b", lower): base += 0.15
    if re.search(r"\blife[- ]?changing\b", lower):   base += 0.20
    if re.search(r"\beverything\b", lower):          base += 0.08
    if re.search(r"\beveryone\b", lower):            base += 0.06
    if re.search(r"\bconsequences?\b", lower):       base += 0.08
    if scene.consequence_severity > 0:
        base += scene.consequence_severity * 0.35

    return max(0.10, min(1.0, base))


def _seed_from(situation: str) -> int:
    h = hashlib.sha256(situation.encode("utf-8")).hexdigest()
    return int(h[:8], 16)


def pick(items: list, seed: int, offset: int = 0):
    if not items:
        return None
    return items[(seed + offset) % len(items)]


# -----------------------------------------------------------------------------
# Public scoring
# -----------------------------------------------------------------------------

def score_scene(scene: Scene) -> int:
    """
    Deterministic score from scene dimensions.
    Weights tuned so most scenarios land in [15, 95], and consequence signals
    set a hard floor that can't be undercut by positive signals.
    """
    urgency = _urgency(scene)
    stakes = scene.stakes
    prep_gap = 0.85 if not scene.user_prepared else 0.15
    uncontrollability = 1.0 - scene.user_control

    raw = (
        urgency           * 0.30 +
        stakes            * 0.30 +
        prep_gap          * 0.20 +
        uncontrollability * 0.20
    )

    # Consequence override — sets a floor
    if scene.consequence_severity > 0:
        raw = max(raw, scene.consequence_severity * 0.98)

    return max(3, min(99, int(round(raw * 100))))


def _urgency(scene: Scene) -> float:
    h = scene.hours_remaining
    if h is None:
        return 0.45
    if h <= 0.5:    return 1.00
    if h <= 3:      return 0.95
    if h <= 8:      return 0.85
    if h <= 24:     return 0.75
    if h <= 48:     return 0.60
    if h <= 168:    return 0.40
    if h <= 720:    return 0.20
    return 0.10


def severity_for_score(score: int) -> str:
    """Moved here from utils/scoring.py to keep scoring co-located."""
    score = max(0, min(100, int(score)))
    if score >= 96: return "BEYOND_REPAIR"
    if score >= 86: return "DEEPLY_COOKED"
    if score >= 71: return "HEAVILY_COOKED"
    if score >= 51: return "MEDIUM_RARE"
    if score >= 31: return "GETTING_WARM"
    if score >= 11: return "SLIGHTLY_COOKED"
    return "NOT_COOKED"


def scene_to_dict(scene: Scene) -> dict:
    """Serialize a Scene for JSON transmission to Groq or logging."""
    return {
        "actors": scene.actors,
        "events": scene.events,
        "primary_event": scene.primary_event,
        "hours_remaining": scene.hours_remaining,
        "deadline_phrase": scene.deadline_phrase,
        "domain": scene.domain,
        "secondary_domains": scene.secondary_domains,
        "stakes": round(scene.stakes, 2),
        "consequence_type": scene.consequence_type,
        "consequence_severity": round(scene.consequence_severity, 2),
        "reversibility": round(scene.reversibility, 2),
        "user_prepared": scene.user_prepared,
        "user_control": round(scene.user_control, 2),
        "detected_phrases": scene.detected_phrases[:10],
    }