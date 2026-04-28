"""Reporting layer — aggregation, formatting, and baseline comparison."""

from balance_framework.reporting.test_report import EncounterSuite, TeamStats, summarize, format_report
from balance_framework.reporting.baseline import (
    save_baseline, load_baseline, diff_baseline, RegressionFlag,
)

__all__ = [
    "EncounterSuite",
    "TeamStats",
    "summarize",
    "format_report",
    "save_baseline",
    "load_baseline",
    "diff_baseline",
    "RegressionFlag",
]
