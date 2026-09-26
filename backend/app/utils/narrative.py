"""
Rules-based narrative generation. Given a parsed Scene and a deterministic
score, produce the human-readable content: diagnosis, reasons, plan, etc.

This is the fallback when Groq is unavailable, AND the source of truth for
the response shape (Groq fills the same fields).
"""
from __future__ import annotations

from typing import Any, Dict, List

from .scene import Scene, pick


# -----------------------------------------------------------------------------
# Diagnosis
# -----------------------------------------------------------------------------

def build_diagnosis(scene: Scene, score: int) -> str:
    parts = [_opener(scene, score), _middle(scene), _closer(scene, score)]
    return " ".join(p for p in parts if p)[:420]


def _opener(scene: Scene, score: int) -> str:
    if scene.consequence_severity >= 0.85:
        return pick([
            "This isn't a scheduling problem. This is a 'what did you do' problem.",
            "You didn't just cook — you took the whole kitchen with you.",
            "This has moved past 'situation' into 'incident report'.",
        ], scene.seed)
    if scene.consequence_severity >= 0.7:
        return pick([
            "The damage is done. The only question is how much.",
            "This is a damage-control problem, not a prep problem.",
            "You're past prevention. Now it's about containment.",
        ], scene.seed, 1)
    if scene.consequence_severity >= 0.5:
        return pick([
            "This one leaves a mark, but it's a mark, not a hole.",
            "You've already done the thing. The next move is what matters.",
        ], scene.seed, 2)

    if scene.primary_event == "feeling":
        return pick([
            "Nothing has happened yet — you're just inside your own head.",
            "This is anxiety, not emergency. The oven isn't even on.",
        ], scene.seed, 3)

    hours = scene.hours_remaining
    domain = scene.domain

    if hours is not None and hours < 3 and not scene.user_prepared:
        return {
            "academic":     "You have under three hours and haven't started. This is a sprint, not a study session.",
            "career":       "You walk into this in under three hours. Preparation is now cosmetic.",
            "relationship": "You have less than three hours before this lands. Rushing will make it worse.",
            "money":        "You have hours, not days. Every decision must be reversible.",
        }.get(domain, "You're inside the final window. Every minute has a different value than the last.")

    if hours is not None and hours < 24 and not scene.user_prepared:
        return {
            "academic":     "You have a day to cover a semester. It's triage, not mastery.",
            "career":       "Tomorrow is close enough to be scary. Tonight is what counts.",
            "relationship": "This has to be handled today, not tomorrow.",
            "money":        "Less than 24 hours of runway. Prioritize survival, not optimization.",
        }.get(domain, "The timeline is tight but not yet lost. Focus matters more than effort.")

    if scene.user_prepared:
        return pick([
            "You've done the work. The panic is louder than the problem.",
            "This is well-prepared. Your nerves are lying to you.",
        ], scene.seed, 4)

    if score >= 80:
        return pick([
            "The oven is preheated and it knows your name.",
            "This is genuinely serious and it's on you to move now.",
        ], scene.seed, 5)
    if score >= 55:
        return pick([
            "There's still time, but it's thinner than you'd like.",
            "This is warm. Not on fire. Yet.",
        ], scene.seed, 6)
    if score >= 30:
        return pick([
            "This is a speedbump, not a wall.",
            "Not a crisis. An annoyance with a deadline.",
        ], scene.seed, 7)
    return pick([
        "Suspiciously under control.",
        "The oven isn't even on. Suspicious.",
    ], scene.seed, 8)


def _middle(scene: Scene) -> str:
    facts = []
    if scene.deadline_phrase and scene.deadline_phrase not in ("next month",):
        facts.append(scene.deadline_phrase)
    if scene.primary_event == "incomplete":
        facts.append("no prep")
    elif scene.primary_event == "feeling":
        facts.append("no concrete event")
    elif scene.consequence_type:
        facts.append(scene.consequence_type.replace("_", " "))
    if not facts:
        return ""
    return f"({', '.join(facts[:2])})"


def _closer(scene: Scene, score: int) -> str:
    if scene.consequence_severity >= 0.7:
        return pick([
            "What you do next matters more than what you did.",
            "There's no clever exit here. Only the honest one.",
        ], scene.seed, 9)
    if scene.user_prepared:
        return "Trust your prep."
    if score >= 80:
        return pick([
            "Move now, and the number drops fast.",
            "The first hour is worth more than the last three.",
        ], scene.seed, 10)
    if score >= 50:
        return pick([
            "You still have options. Fewer than yesterday, more than tomorrow.",
            "Start in the next ten minutes or lose the window.",
        ], scene.seed, 11)
    return "You'll be fine."


# -----------------------------------------------------------------------------
# Reasons
# -----------------------------------------------------------------------------

def build_reasons(scene: Scene, score: int) -> List[Dict[str, str]]:
    reasons: List[Dict[str, str]] = []

    domain_reason = {
        "academic":     ("📚", "Academic runway is short"),
        "career":       ("💼", "Career exposure"),
        "relationship": ("❤️", "Relationship at risk"),
        "money":        ("💰", "Financial runway compressed"),
        "technology":   ("💻", "Technical setup unstable"),
        "social":       ("🗣️", "Social consequence in play"),
        "legal":        ("⚖️", "Legal exposure"),
        "health":       ("🩺", "Health risk"),
        "other":        ("🎯", "Situation under-specified"),
    }
    if scene.domain in domain_reason:
        e, l = domain_reason[scene.domain]
        reasons.append({"emoji": e, "label": l})

    if scene.consequence_type:
        reasons.append({
            "emoji": "⚠️",
            "label": scene.consequence_type.replace("_", " ").title(),
        })

    if scene.hours_remaining is not None:
        if scene.hours_remaining < 6:
            reasons.append({"emoji": "⏰", "label": "Hours, not days"})
        elif scene.hours_remaining < 48:
            reasons.append({"emoji": "⏰", "label": "A day or less"})
        elif scene.hours_remaining < 240:
            reasons.append({"emoji": "📅", "label": "Less than a week"})

    if not scene.user_prepared and scene.primary_event not in (
        "feeling", "conflict", "mistake"
    ):
        reasons.append({"emoji": "📉", "label": "Preparation is minimal"})

    if scene.reversibility < 0.5:
        reasons.append({"emoji": "🔒", "label": "Not easily reversed"})

    if scene.stakes >= 0.85:
        reasons.append({"emoji": "🚨", "label": "High stakes"})

    if "authority" in scene.actors or "professor" in scene.actors:
        reasons.append({"emoji": "👤", "label": "Authority figure involved"})
    if len(scene.actors) >= 2:
        reasons.append({"emoji": "👥", "label": "Multiple people affected"})

    if len(reasons) < 2:
        reasons.append({"emoji": "❓", "label": "Details are thin"})

    return reasons[:5]


# -----------------------------------------------------------------------------
# Risks
# -----------------------------------------------------------------------------

def build_risks(scene: Scene) -> List[str]:
    risks: List[str] = []

    if scene.reversibility < 0.4:
        risks.append("Damage may outlast the event")
    if scene.hours_remaining is not None and scene.hours_remaining < 12:
        risks.append("No meaningful buffer left")
    if not scene.user_prepared and scene.primary_event in (
        "exam", "interview", "presentation", "deadline", "assignment"
    ):
        risks.append("Starting from zero")
    if scene.stakes >= 0.8:
        risks.append("Ripple effects across multiple areas")
    if scene.domain == "money":
        risks.append("Runway shrinks with every hour")
    if scene.domain == "career":
        risks.append("First impressions set long-term trajectories")
    if scene.domain == "relationship":
        risks.append("Silence reads as guilt")
    if scene.consequence_severity >= 0.7:
        risks.append("Consequences may be documented")
        risks.append("Second-order effects likely")

    if not risks:
        risks.append("No acute risk detected")
        risks.append("Situation may be under-reported")

    return risks[:5]


# -----------------------------------------------------------------------------
# Plan
# -----------------------------------------------------------------------------

def build_plan(scene: Scene, score: int) -> List[str]:
    if scene.consequence_severity >= 0.85:
        return [
            "Stop. Do not argue, explain, or defend.",
            "Own exactly what you did in one sentence. No hedging.",
            "Apologize once, in writing, without bargaining.",
            "Accept the immediate consequence without resistance.",
            "Ask what would help. Then listen.",
            "Give it time. Do not chase reassurance.",
        ]
    if scene.consequence_severity >= 0.6:
        return [
            "Acknowledge the mistake to the person affected.",
            "Fix what can be fixed today. Note what can't.",
            "Let the situation settle before deciding anything else.",
            "Write the lesson in one sentence — future-you needs it.",
        ]

    domain = scene.domain
    emergency = score >= 75
    prepared = scene.user_prepared

    if domain == "academic":
        if prepared:
            return [
                "Skim your own notes — trust what you already built.",
                "Do one practice problem end-to-end.",
                "Sleep. Recall beats cramming at this point.",
            ]
        if emergency:
            return [
                "Rank topics by weight in the exam, not by interest.",
                "Start with the highest-weight topic. Do not stop for polish.",
                "Write a 5-line summary of each concept — memory over mastery.",
                "25 minutes work, 5 off. Do not skip breaks.",
                "Skip anything you already know cold.",
            ]
        return [
            "Skim headings first to build a map.",
            "Pick the top three concepts and go deep, not wide.",
            "Do one full past-paper question.",
            "Then revise only what you got wrong.",
        ]

    if domain == "career":
        if prepared:
            return [
                "Prepare three thoughtful questions to ask them.",
                "Run the first 60 seconds of your answer out loud once.",
                "Leave 10 minutes early. Rushing reads as nerves.",
            ]
        return [
            "Reread the job description and pick 3 talking points.",
            "Write one story for 'tell me about yourself'.",
            "Prepare two questions that show you read the material.",
            "Sleep. Nerves beat exhaustion every time.",
        ]

    if domain == "relationship":
        return [
            "Write the message you wish you'd sent. Don't send it yet.",
            "Wait 10 minutes. Reread it. Send the calmer version.",
            "If it escalates, ask to talk on a call instead of text.",
            "Own your part. Do not litigate theirs.",
        ]

    if domain == "money":
        return [
            "List every payment due before the next inflow.",
            "Cut everything that isn't rent, food, or transport.",
            "Ask one trusted person for help today — not next week.",
            "Do not take on new debt to pay old debt.",
        ]

    if domain == "technology":
        return [
            "Isolate the failure. Change one variable at a time.",
            "Read the actual error before guessing.",
            "Roll back to the last known-good state if possible.",
            "Ask for help after 20 minutes, not 2 hours.",
        ]

    if domain == "legal":
        return [
            "Do not discuss the situation publicly.",
            "Write down what happened, factually, for your own memory.",
            "Talk to someone qualified before acting.",
            "Do not negotiate or apologize on impulse.",
        ]

    if domain == "social":
        return [
            "Own the mistake plainly. No joke, no deflection.",
            "Offer a specific fix, not a vague apology.",
            "Then stop. Over-explaining reads as guilt.",
        ]

    if domain == "health":
        return [
            "Tell someone you trust. Do not manage this alone.",
            "Follow professional advice. This isn't a willpower problem.",
            "Sleep, eat, hydrate. Basics first.",
        ]

    if score >= 70:
        return [
            "Stop everything unrelated to the critical path.",
            "Pick ONE task that unblocks the rest.",
            "Work in 25-minute blocks. Reassess between.",
            "Sleep tonight. Tomorrow is worse without it.",
        ]
    return [
        "Identify the smallest useful next action.",
        "Do that one thing. Then reassess.",
    ]


# -----------------------------------------------------------------------------
# Emergency
# -----------------------------------------------------------------------------

def build_emergency(scene: Scene, score: int) -> List[str]:
    if score < 70 and scene.consequence_severity < 0.6:
        return []

    if scene.consequence_severity >= 0.7:
        return [
            "Do not send another message tonight.",
            "Do not call to argue your side.",
            "Write down what happened, factually, for yourself.",
            "Tell one trusted person so you don't spiral alone.",
            "Sleep. Decisions made in panic are worse decisions.",
        ]

    if scene.domain == "academic":
        return [
            "Phone in another room. Timer visible.",
            "Work only on the highest-weight topic.",
            "Skip everything you already know.",
            "25 minutes on, 5 off. No exceptions.",
        ]
    if scene.domain == "career":
        return [
            "Prepare the 3 questions you'll ask.",
            "Say your first 60 seconds out loud.",
            "Close every tab that isn't the job description.",
        ]
    if scene.domain == "money":
        return [
            "List the next 5 payments in order.",
            "Call anyone you owe before they call you.",
            "Pause every subscription today.",
        ]

    return [
        "Close all non-essential tabs and apps.",
        "Phone in another room.",
        "25-minute timer. One task only.",
    ]


# -----------------------------------------------------------------------------
# Commentary
# -----------------------------------------------------------------------------

def build_commentary(scene: Scene, score: int) -> str:
    if scene.consequence_severity >= 0.7:
        return pick([
            "You didn't just burn the bridge. You ordered it well-done.",
            "The oven is the least of your problems.",
            "This isn't a cooking situation. It's a cleanup situation.",
        ], scene.seed, 12)
    if score >= 96:
        return "Congratulations. You have achieved maximum cook."
    if score >= 86:
        return pick([
            "Bro is not medium rare anymore. Bro is charcoal.",
            "The fire department has been notified.",
            "Somewhere a smoke alarm just went off.",
        ], scene.seed)
    if score >= 71:
        return pick([
            "The oven is preheated. The chicken has accepted its fate.",
            "The heat is on and it's personal.",
        ], scene.seed, 13)
    if score >= 51:
        return pick([
            "The oven is warm. The chicken is nervous.",
            "You're cooking, not burnt. Yet.",
        ], scene.seed, 14)
    if score >= 31:
        return pick([
            "You might actually survive this. Don't get cocky.",
            "You're simmering. Not boiling.",
        ], scene.seed, 15)
    return pick([
        "The oven isn't even on. Show-off.",
        "You're room temperature.",
    ], scene.seed, 16)


# -----------------------------------------------------------------------------
# What happens next
# -----------------------------------------------------------------------------

def build_what_next(scene: Scene, score: int) -> List[Dict[str, str]]:
    if scene.consequence_severity >= 0.7:
        return [
            {"when": "In 30 minutes", "what": "You will reread the message and cringe."},
            {"when": "Tonight",       "what": "You will rehearse an explanation."},
            {"when": "Tomorrow",      "what": "You will either apologize properly or avoid it. Pick one."},
            {"when": "This week",     "what": "You will learn whether this is a speedbump or a scar."},
        ]

    domain = scene.domain
    hours = scene.hours_remaining

    if score >= 86 and hours is not None and hours < 24:
        return [
            {"when": "In 10 minutes", "what": "You will open one more tab 'just to check'."},
            {"when": "In 45 minutes", "what": _impulse_for(domain)},
            {"when": "In 2 hours",    "what": "You will remember you have a body that needs water."},
            {"when": "Tonight",       "what": "You will either fix one thing or fall asleep trying."},
            {"when": "Tomorrow",      "what": "You will promise yourself this never happens again."},
        ]

    if score >= 55:
        return [
            {"when": "In 15 minutes", "what": "You will start. Slowly."},
            {"when": "In 1 hour",     "what": "You will be surprised by your own progress."},
            {"when": "Tonight",       "what": "You will wonder why you panicked."},
        ]
    if score >= 30:
        return [
            {"when": "In 30 minutes", "what": "You will finish ahead of schedule."},
            {"when": "Later today",   "what": "You will take an unearned victory lap."},
        ]
    return [
        {"when": "In 1 hour", "what": "You will forget this app exists."},
        {"when": "Tomorrow",  "what": "You will tell everyone you 'wasn't even stressed'."},
    ]


def _impulse_for(domain: str) -> str:
    return {
        "academic":     "You will open YouTube 'for background music'.",
        "career":       "You will reread the same line in the job description three times.",
        "relationship": "You will draft a message and delete it three times.",
        "money":        "You will redo the same math hoping it changes.",
        "technology":   "You will close and reopen the terminal, hoping.",
        "social":       "You will type a reply and not send it.",
    }.get(domain, "You will open one more tab 'just to check'.")


# -----------------------------------------------------------------------------
# Orchestrator
# -----------------------------------------------------------------------------

def rules_narrate(scene: Scene, score: int) -> Dict[str, Any]:
    return {
        "diagnosis": build_diagnosis(scene, score),
        "reasons": build_reasons(scene, score),
        "risk_factors": build_risks(scene),
        "recovery_plan": build_plan(scene, score),
        "emergency_actions": build_emergency(scene, score),
        "funny_commentary": build_commentary(scene, score),
        "what_happens_next": build_what_next(scene, score),
    }