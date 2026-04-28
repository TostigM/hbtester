"""Runner layer — batch encounter execution and result collection."""

from balance_framework.runner.seeding import seed_range
from balance_framework.runner.collector import EncounterResult, CombatantResult, collect_result
from balance_framework.runner.orchestrator import run_encounter_batch

__all__ = [
    "seed_range",
    "EncounterResult",
    "CombatantResult",
    "collect_result",
    "run_encounter_batch",
]
