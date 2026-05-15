"""Decision records — what action a combatant chose and why."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class DecisionRecord:
    """One combatant's action choice for a single turn."""
    round_number: int
    combatant_id: str
    behavior_profile: str
    action_types: list[str]   # e.g. ["weapon_attack", "weapon_attack"]
    target_ids: list[str]     # parallel list of target IDs (empty string = no target)
    rationale: str = ""       # brief human-readable note


@dataclass
class DecisionLog:
    """Accumulates decision records for one encounter."""
    records: list[DecisionRecord] = field(default_factory=list)

    def record(
        self,
        round_number: int,
        combatant_id: str,
        behavior_profile: str,
        actions: list,
        rationale: str = "",
    ) -> None:
        """Append a record for *actions* (list of Action dataclasses)."""
        self.records.append(DecisionRecord(
            round_number=round_number,
            combatant_id=combatant_id,
            behavior_profile=behavior_profile,
            action_types=[getattr(a, "action_type", "unknown") for a in (actions or [])],
            target_ids=[getattr(a, "target_id", getattr(a, "combatant_id", "")) for a in (actions or [])],
            rationale=rationale,
        ))

    def for_combatant(self, combatant_id: str) -> list[DecisionRecord]:
        return [r for r in self.records if r.combatant_id == combatant_id]

    def for_round(self, round_number: int) -> list[DecisionRecord]:
        return [r for r in self.records if r.round_number == round_number]
