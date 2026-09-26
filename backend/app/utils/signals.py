"""
Signal extraction for the mock provider. Reads the raw situation string
and returns a structured summary of what's going on, so scoring and content
generation can be reactive rather than generic.

Everything here is deterministic — the same input always produces the
same signals. No AI, no randomness, no external calls.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from typing import List


# -----------------------------------------------------------------------------
# Signal tables
# -----------------------------------------------------------------------------

TIME_SIGNALS = [
    (r"\bin \d+ ?(minute|min|hour|hr)s?\b", 22, "minutes/hours away"),
    (r"\btomorrow\b",                         18, "tomorrow"),
    (r"\btonight\b",                          18, "tonight"),
    (r"\btoday\b",                            16, "today"),
    (r"\bnext week\b",                         6, "next week"),
    (r"\bnext month\b",                        2, "next month"),
    (r"\balready late\b|\bi'?m late\b|\brunning late\b", 25, "already late"),
    (r"\bdeadline is (today|tonight|tomorrow)\b", 20, "deadline imminent"),
    (r"\b(no time left|out of time)\b",        28, "no time left"),
]

PREP_SIGNALS = [
    (r"\bhaven'?t (started|studied|prepared|begun)\b", 20, "not started"),
    (r"\bhaven'?t (read|opened|touched)\b",           16, "not touched"),
    (r"\bdon'?t know where to start\b",               12, "no starting point"),
    (r"\bforgot(ten)?\b",                             10, "forgot"),
    (r"\bprocrastinat",                               14, "procrastinated"),
    (r"\bwasted (the )?(whole|entire) (day|week|weekend)\b", 15, "wasted time"),
    (r"\b(still )?(don'?t|no) (have|has) (a )?plan\b",  10, "no plan"),
    (r"\bjust (started|began|learned) (learning )?\w+",  14, "just started"),
]

SITUATION_SIGNALS = [
    # Financial squeeze
    (r"\b(only |just )?\d+ ?(rupees|dollars|euros|pounds|bucks) (left|remaining)\b", 20, "low on funds"),
    (r"\b(broke|zero balance|no money)\b",                                    18, "out of money"),
    (r"\bpayday is \d+ days away\b|\bpayday.*\bweeks? away\b",                18, "long gap to payday"),

    # Misstep
    (r"\baccidentally\b|\bby mistake\b|\boops\b",                             15, "accident"),

    # Compounded mess
    (r"\b(and now|and then|and on top of that)\b",                            6,  "compounding"),
]

# Consequence signals — events that already happened and carry weight.
# These OVERRIDE the base score regardless of time/prep signals.
CONSEQUENCE_SIGNALS = [
    # Violence / physical
    (r"\b(slap(ped)?|hit|punched|punch(ed)?|pushed|shoved|kicked)\b",   40, "physical altercation"),

    # Verbal / reputational damage to authority
    (r"\b(yelled at|shouted at|insulted|cursed at|swore at|told off)\b", 30, "verbal altercation"),
    (r"\b(principal|headmaster|dean|director|ceo|police|officer|cop|judge|boss)\b.*\b(slap|hit|yell|insult|curs|swear|fight|argue)\w*\b", 45, "confronted authority"),
    (r"\b(slap|hit|yell|insult|curs|swear|fight|argue)\w*\b.*\b(principal|headmaster|dean|director|ceo|police|officer|cop|judge|boss)\b", 45, "confronted authority"),

    # Legal / disciplinary
    (r"\b(police|arrested|charged|fir|complaint|lawsuit|court|summons|expelled|suspended|fired|terminated)\b", 35, "legal/disciplinary"),

    # Cheating / academic integrity
    (r"\b(cheat(ed|ing)?|plagiar|caught copying)\b",                    25, "academic integrity"),

    # Relationship breach
    (r"\b(cheated|betrayed|lied to (everyone|her|him|them))\b",         25, "trust breach"),

    # Money gone wrong (big)
    (r"\b(lost (all|the) (my )?money|scammed|gambled away|spent everything)\b", 30, "financial disaster"),

    # Health / safety
    (r"\b(overdose|hospital(ized)?|passed out|fainted|broke my|fractured)\b", 30, "health emergency"),
]

DOMAIN_SIGNALS = {
    "academic": [
        r"\bexam\b", r"\btest\b", r"\bquiz\b", r"\bassignment\b", r"\bhomework\b",
        r"\bprofessor\b", r"\bteacher\b", r"\bclass\b", r"\bcourse\b",
        r"\bgrade\b", r"\bsemester\b", r"\bsyllabus\b", r"\bthesis\b",
        r"\bproject\b", r"\bdue (friday|monday|tomorrow|tonight)\b",
        r"\bprincipal\b", r"\bheadmaster\b", r"\bdean\b", r"\bexpelled\b", r"\bsuspended\b",
    ],
    "career": [
        r"\binterview\b", r"\bjob\b", r"\bboss\b", r"\bmanager\b", r"\bclient\b",
        r"\bpromotion\b", r"\bresume\b", r"\bcv\b", r"\boffer\b", r"\bhr\b",
        r"\bmeeting\b", r"\bpresentation\b", r"\bstandup\b",
    ],
    "relationship": [
        r"\bgirlfriend\b", r"\bboyfriend\b", r"\bwife\b", r"\bhusband\b",
        r"\bpartner\b", r"\bcrush\b", r"\bex\b", r"\bbreakup\b",
        r"\banniversary\b", r"\bdate\b", r"\bvalentine\b",
    ],
    "money": [
        r"\bmoney\b", r"\bcash\b", r"\bbroke\b", r"\bpayday\b", r"\bsalary\b",
        r"\brent\b", r"\bbill\b", r"\bloan\b", r"\bdebt\b", r"\bbudget\b",
        r"₹", r"\$", r"€", r"£",
        r"\brupees?\b", r"\bdollars?\b", r"\beuros?\b", r"\bpounds?\b",
    ],
    "technology": [
        r"\bcode\b", r"\bpython\b", r"\bjava\b", r"\bjavascript\b", r"\breact\b",
        r"\bapi\b", r"\bserver\b", r"\bdatabase\b", r"\bbug\b", r"\bdeploy\b",
        r"\blaptop\b", r"\bwindows\b", r"\bupdate\b", r"\bcomputer\b",
        r"\bsoftware\b", r"\bcompile\b", r"\bgithub\b", r"\bcharger\b",
        r"\bbattery\b", r"\bphone.*\d+%\b",
    ],
    "social": [
        r"\btexted\b", r"\bmessage\b", r"\bgroup chat\b", r"\bwhatsapp\b",
        r"\binstagram\b", r"\btweet\b", r"\bposted\b", r"\bcomment\b",
        r"\breply\b", r"\bstory\b", r"\bdm\b", r"\bscreenshot\b",
        r"\bslapped\b", r"\bpunched\b", r"\byelled at\b", r"\bfight\b", r"\bfought\b",
    ],
    "time": [
        r"\blate\b", r"\bdeadline\b", r"\bschedule\b", r"\bcalendar\b",
        r"\bappointment\b", r"\bmissed\b",
    ],
}

RISK_SIGNALS = [
    (r"\bfinal\b",                8,  "final exam/stage"),
    (r"\bcritical\b",             6,  "critical"),
    (r"\bcareer[- ]?defining\b",  8,  "career-defining"),
    (r"\blife[- ]?changing\b",    8,  "life-changing"),
    (r"\beverything\b",           4,  "broad stakes"),
    (r"\beveryone\b",             4,  "broad stakes"),
    (r"\b(2|3|4|5) different\b",  6,  "multiple parties involved"),
    (r"\bconsequences\b",         4,  "consequences"),
]

POSITIVE_SIGNALS = [
    (r"\bi (have |had |'ve )?(already )?(prepared|studied|planned|started|finished|revised)\b", 22, "prepared"),
    (r"\bi'?m ready\b|\ball set\b|\bi am ready\b",    18, "ready"),
    (r"\bi have a plan\b|\bi'?ve got a plan\b",       14, "has plan"),
    (r"\bhalfway\b|\bmostly done\b|\balmost done\b",  10, "partially done"),
    (r"\bplenty of time\b|\bnot due (for|until)\b",   18, "time available"),
    (r"\bi'?m just (worried|nervous|overthinking)\b", 10, "overthinking"),
]


# -----------------------------------------------------------------------------
# Data class
# -----------------------------------------------------------------------------

@dataclass
class Signals:
    raw: str
    category: str = "other"
    score_delta: int = 0
    consequence_weight: int = 0
    time_pressure: str | None = None
    prep_state: str | None = None
    matched_phrases: List[str] = field(default_factory=list)
    risk_notes: List[str] = field(default_factory=list)
    positive_notes: List[str] = field(default_factory=list)
    seed: int = 0


# -----------------------------------------------------------------------------
# Main entry
# -----------------------------------------------------------------------------

def extract_signals(situation: str) -> Signals:
    text = (situation or "").lower()
    sig = Signals(raw=situation, seed=_seed_from(situation))

    # --- Time pressure ---
    best_time = 0
    for pattern, weight, label in TIME_SIGNALS:
        if re.search(pattern, text):
            if weight > best_time:
                best_time = weight
                sig.time_pressure = label
            sig.matched_phrases.append(label)
    sig.score_delta += best_time

    # --- Prep state ---
    best_prep = 0
    for pattern, weight, label in PREP_SIGNALS:
        if re.search(pattern, text):
            if weight > best_prep:
                best_prep = weight
                sig.prep_state = label
            sig.matched_phrases.append(label)
    sig.score_delta += best_prep

    # --- Situation-specific pain signals ---
    best_sit = 0
    for pattern, weight, label in SITUATION_SIGNALS:
        if re.search(pattern, text):
            if weight > best_sit:
                best_sit = weight
            sig.matched_phrases.append(label)
    sig.score_delta += best_sit

    # --- Category detection ---
    cat_scores = {}
    for cat, patterns in DOMAIN_SIGNALS.items():
        hits = sum(1 for p in patterns if re.search(p, text))
        if hits:
            cat_scores[cat] = hits
    if cat_scores:
        sig.category = max(cat_scores, key=cat_scores.get)
        sig.matched_phrases.append(sig.category)

    # --- Risk signals ---
    for pattern, weight, label in RISK_SIGNALS:
        if re.search(pattern, text):
            sig.score_delta += weight
            sig.risk_notes.append(label)

    # --- Consequence signals — set a floor on the score ---
    top_consequence = 0
    for pattern, weight, label in CONSEQUENCE_SIGNALS:
        if re.search(pattern, text):
            if weight > top_consequence:
                top_consequence = weight
            sig.risk_notes.append(label)
    sig.consequence_weight = top_consequence

    # --- Positive signals (with negation guard) ---
    for pattern, weight, label in POSITIVE_SIGNALS:
        m = re.search(pattern, text)
        if m:
            start = max(0, m.start() - 15)
            window = text[start:m.start()]
            if re.search(r"(?:not|n'?t|never|no)\s*$", window):
                continue
            sig.score_delta -= weight
            sig.positive_notes.append(label)

    # --- Fallback for vague inputs ---
    if sig.category == "other" and not sig.time_pressure and not sig.prep_state:
        sig.score_delta += 8

    return sig


def _seed_from(situation: str) -> int:
    h = hashlib.sha256(situation.encode("utf-8")).hexdigest()
    return int(h[:8], 16)


def pick(items: list, seed: int, offset: int = 0):
    if not items:
        return None
    return items[(seed + offset) % len(items)]