from typing import List

WELLBEING_PLAYBOOKS = {
    "grounding": [
        "Name 5 things you see, 4 you can touch, 3 you hear, 2 you smell, 1 you taste.",
        "Slow exhale: breathe out for 6-8 seconds, then in for 4. Repeat 5 times.",
    ],
    "stress_reset": [
        "Take a 2-minute walk if safe, stretch shoulders/neck, sip water.",
        "Define the next tiny task you can finish in 5 minutes; do only that.",
    ],
    "conflict_script": [
        "Use a calm opener: “Can we talk about the task? I want to avoid mistakes.”",
        "State facts, not motives: describe what happened and how it affects safety/schedule.",
        "Ask for their view, then agree on one concrete next step.",
    ],
    "sleep_hygiene": [
        "Avoid caffeine 6 hours before sleep; keep room dark and cool.",
        "If your mind races, write a 3-bullet list of worries and plan to revisit tomorrow.",
    ],
}


def wellbeing_response(feeling: str | None = None) -> str:
    parts: List[str] = [
        "I’m here as an AI support tool, not a therapist. I can share short coping ideas.",
        "Pick what feels helpful; skip anything that doesn’t.",
    ]
    if feeling:
        parts.append(f"I hear you mentioning {feeling}.")
    parts.append("Grounding ideas:")
    parts.extend([f"- {step}" for step in WELLBEING_PLAYBOOKS["grounding"]])
    parts.append("Stress reset ideas:")
    parts.extend([f"- {step}" for step in WELLBEING_PLAYBOOKS["stress_reset"]])
    parts.append("If this involves conflict on-site, a respectful script:")
    parts.extend([f"- {step}" for step in WELLBEING_PLAYBOOKS["conflict_script"]])
    parts.append("If sleep is an issue, consider:")
    parts.extend([f"- {step}" for step in WELLBEING_PLAYBOOKS["sleep_hygiene"]])
    parts.append("If you feel unsafe or overwhelmed, talk to a supervisor or trusted person.")
    return "\n".join(parts)

