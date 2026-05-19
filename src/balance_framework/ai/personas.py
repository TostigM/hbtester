"""LLM persona definitions and upfront strategy generation via Claude Haiku."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass


PERSONAS: dict[str, dict] = {
    "power_gamer": {
        "display_name": "Power Gamer",
        "description": (
            "A highly optimized player who squeezes maximum mechanical value from every turn. "
            "Always uses the best available action, never forgets a bonus action, and focuses "
            "fire on the lowest-HP enemy to secure kills efficiently."
        ),
    },
    "newbie": {
        "display_name": "Newbie",
        "description": (
            "A new player still learning the rules. Often forgets bonus actions, "
            "picks targets somewhat randomly, and may not use class features optimally."
        ),
    },
    "veteran": {
        "display_name": "Veteran",
        "description": (
            "An experienced player who plays consistently well. Reliably uses bonus actions "
            "and class features, focuses fire intelligently, and manages resources wisely."
        ),
    },
    "forever_dm": {
        "display_name": "Forever DM",
        "description": (
            "A player who usually runs the game as DM and plays cautiously when they do play. "
            "Knows all the rules deeply but is conservative, preferring safe plays over risky ones."
        ),
    },
    "min_maxer": {
        "display_name": "Min-Maxer",
        "description": (
            "A player who hyper-focuses on a single optimized win condition and executes "
            "it with extreme reliability, but may tunnel-vision and miss situational options."
        ),
    },
}


@dataclass
class PersonaStrategy:
    persona_id: str
    display_name: str
    bonus_action_reliability: float  # 0.0–1.0: how often they use their bonus action
    target_priority: str             # "nearest" | "lowest_hp" | "random"
    notes: str                       # LLM-generated tactical summary for display


def generate_persona_strategy(
    persona_id: str,
    class_id: str,
    subclass_id: str | None,
    level: int,
    feature_names: list[str],
) -> PersonaStrategy:
    """Call Claude Haiku once to generate behavioral parameters for this persona + build.

    Falls back to hardcoded defaults if the API key is missing or the call fails.
    """
    persona = PERSONAS.get(persona_id)
    if persona is None:
        raise ValueError(f"Unknown persona {persona_id!r}. Valid: {sorted(PERSONAS)}")

    _load_dotenv()
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return _fallback_strategy(persona_id, persona)

    try:
        return _call_haiku(persona_id, persona, class_id, subclass_id, level, feature_names, api_key)
    except Exception:
        return _fallback_strategy(persona_id, persona)


def _call_haiku(
    persona_id: str,
    persona: dict,
    class_id: str,
    subclass_id: str | None,
    level: int,
    feature_names: list[str],
    api_key: str,
) -> PersonaStrategy:
    import anthropic

    client = anthropic.Anthropic(api_key=api_key)
    features_str = ", ".join(feature_names) if feature_names else "standard class features"
    subclass_str = subclass_id or "none"

    prompt = f"""You are configuring a combat AI for a D&D 5e simulation.

Character: {class_id} (subclass: {subclass_str}), level {level}
Active features: {features_str}

Persona: {persona['display_name']}
{persona['description']}

Return ONLY a JSON object with exactly these three fields:
{{
  "bonus_action_reliability": <float 0.0 to 1.0>,
  "target_priority": <"nearest" or "lowest_hp" or "random">,
  "notes": <string, 1-2 sentences on how this persona plays this specific build>
}}

bonus_action_reliability: how reliably this persona uses their bonus action (0.0=never, 1.0=always).
target_priority: how they choose attack targets.
notes: concise description specific to this build and persona combination.

Return JSON only, no other text."""

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=256,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = message.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    data = json.loads(raw)

    return PersonaStrategy(
        persona_id=persona_id,
        display_name=persona["display_name"],
        bonus_action_reliability=float(data["bonus_action_reliability"]),
        target_priority=str(data["target_priority"]),
        notes=str(data.get("notes", "")),
    )


_FALLBACK_PARAMS: dict[str, dict] = {
    "power_gamer": {"bonus_action_reliability": 0.97, "target_priority": "lowest_hp"},
    "veteran":     {"bonus_action_reliability": 0.90, "target_priority": "lowest_hp"},
    "forever_dm":  {"bonus_action_reliability": 0.85, "target_priority": "nearest"},
    "min_maxer":   {"bonus_action_reliability": 0.80, "target_priority": "lowest_hp"},
    "newbie":      {"bonus_action_reliability": 0.40, "target_priority": "random"},
}


def _fallback_strategy(persona_id: str, persona: dict) -> PersonaStrategy:
    params = _FALLBACK_PARAMS.get(persona_id, {"bonus_action_reliability": 0.85, "target_priority": "nearest"})
    return PersonaStrategy(
        persona_id=persona_id,
        display_name=persona["display_name"],
        bonus_action_reliability=params["bonus_action_reliability"],
        target_priority=params["target_priority"],
        notes="(Haiku unavailable — using fallback defaults)",
    )


def _load_dotenv() -> None:
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
