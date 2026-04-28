"""Reporting layer — aggregation, formatting, and baseline comparison."""

from balance_framework.reporting.test_report import EncounterSuite, TeamStats, summarize, format_report
from balance_framework.reporting.baseline import (
    save_baseline, load_baseline, diff_baseline, RegressionFlag,
)
from balance_framework.reporting.visualizations import (
    ascii_histogram, rounds_histogram, hp_fraction_histogram, damage_histogram,
)
from balance_framework.reporting.formats.markdown import format_suite_markdown
from balance_framework.reporting.formats.csv import write_encounter_csv, write_combatant_csv
from balance_framework.reporting.formats.json import write_results, read_results, write_suite

__all__ = [
    # Core
    "EncounterSuite", "TeamStats", "summarize", "format_report",
    # Baseline
    "save_baseline", "load_baseline", "diff_baseline", "RegressionFlag",
    # Visualizations
    "ascii_histogram", "rounds_histogram", "hp_fraction_histogram", "damage_histogram",
    # Markdown
    "format_suite_markdown",
    # CSV
    "write_encounter_csv", "write_combatant_csv",
    # JSON
    "write_results", "read_results", "write_suite",
]
