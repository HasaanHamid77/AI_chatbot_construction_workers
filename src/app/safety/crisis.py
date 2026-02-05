from __future__ import annotations

from dataclasses import dataclass
from typing import List

from app.config import get_settings


@dataclass
class CrisisSignal:
    triggered: bool
    matched_terms: List[str]


def detect_crisis(text: str) -> CrisisSignal:
    """
    Lightweight lexicon match for crisis-related language.
    Conservative: any match triggers escalation path.
    """
    settings = get_settings()
    lexicon = [w.strip().lower() for w in settings.crisis_keywords.split(",") if w.strip()]
    lower = text.lower()
    hits = [term for term in lexicon if term in lower]
    return CrisisSignal(triggered=bool(hits), matched_terms=hits)


CRISIS_TEMPLATE = (
    "{disclosure} I’m concerned by what you shared. I can’t provide emergency "
    "help or instructions. If you’re in immediate danger or thinking about "
    "hurting yourself or someone else, please contact local emergency services "
    "or talk to a trusted supervisor/safety officer right now. "
    "You’re not alone, and getting human help quickly is important."
)

