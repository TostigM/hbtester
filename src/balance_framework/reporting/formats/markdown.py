"""Markdown report rendering for encounter suites and subclass comparisons."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from balance_framework.reporting.test_report import EncounterSuite
    from balance_framework.harnesses.subclass import SubclassComparison


def _pct(v: float) -> str:
    return f"{v * 100:.1f}%"


def _tbl_row(*cells: str) -> str:
    return "| " + " | ".join(cells) + " |"


def _tbl_sep(*widths: int) -> str:
    return "| " + " | ".join("-" * max(w, 3) for w in widths) + " |"


def format_suite_markdown(suite: "EncounterSuite", title: str = "Encounter Suite") -> str:
    """Render *suite* as a GitHub-flavoured Markdown document."""
    lines: list[str] = [
        f"# {title}",
        "",
        "## Summary",
        "",
        f"| Metric | Value |",
        "| --- | --- |",
        f"| Encounters | {suite.n} |",
        f"| Timed out | {suite.timed_out} |",
        f"| Avg rounds | {suite.avg_rounds:.1f} ± {suite.std_rounds:.1f} |",
        "",
        "## Results by team",
        "",
        "| Team | Win rate | Avg survivors | Avg HP fraction |",
        "| --- | --- | --- | --- |",
    ]
    for team, ts in sorted(suite.teams.items()):
        lines.append(
            f"| {team} | {_pct(ts.win_rate)} | {ts.avg_survivors:.1f} | {_pct(ts.avg_hp_fraction)} |"
        )
    return "\n".join(lines)


def format_comparison_markdown(comparison: "SubclassComparison") -> str:
    """Render a side-by-side subclass comparison as Markdown."""
    a, b = comparison.variant_a, comparison.variant_b

    lines: list[str] = [
        "# Subclass Comparison",
        "",
        f"Comparing **{a.label}** vs **{b.label}**.",
        "",
        "## Win rate & combat length",
        "",
        "| Variant | Win rate | Avg rounds | Avg rounds ± σ |",
        "| --- | --- | --- | --- |",
    ]
    for v in (a, b):
        wr = _pct(v.suite.win_rate("party"))
        ar = f"{v.suite.avg_rounds:.1f}"
        std = f"{v.suite.avg_rounds:.1f} ± {v.suite.std_rounds:.1f}"
        lines.append(f"| {v.label} | {wr} | {ar} | {std} |")

    lines += [
        "",
        "## Per-combatant stats (variant character)",
        "",
        "| Variant | Avg DMG | Avg kills | Avg healing | Survival |",
        "| --- | --- | --- | --- | --- |",
    ]
    for v in (a, b):
        cs = v.combatant_stats.get("variant")
        if cs is None:
            lines.append(f"| {v.label} | — | — | — | — |")
        else:
            lines.append(
                f"| {v.label} | {cs.avg_damage_dealt:.1f} | {cs.avg_kills:.2f}"
                f" | {cs.avg_healing_done:.1f} | {_pct(cs.survival_rate)} |"
            )

    return "\n".join(lines)
