"""CLI command for subclass YAML analysis — format check + simulation coverage."""

from __future__ import annotations

from pathlib import Path

import click


@click.command()
@click.argument("yaml_file", type=click.Path(exists=True, dir_okay=False))
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON report.")
def analyze(yaml_file: str, as_json: bool) -> None:
    """Analyze a subclass YAML for format validity and simulation coverage.

    Reports which features are fully simulated, partially simulated, or ignored
    by the heuristic test engine, and why.
    """
    from balance_framework.reporting.analyzer import analyze_subclass_yaml
    import json as _json

    text = Path(yaml_file).read_text(encoding="utf-8")
    report = analyze_subclass_yaml(text)

    if as_json:
        click.echo(_json.dumps(report, indent=2))
        raise SystemExit(0 if report["valid"] else 1)

    # ── Human-readable output ──────────────────────────────────────────────

    # Parse / schema errors first
    if report["parse_error"]:
        click.secho(f"\n  PARSE ERROR  {yaml_file}", fg="red", bold=True)
        click.secho(f"  {report['parse_error']}", fg="red")
        raise SystemExit(1)

    if report["schema_errors"]:
        click.secho(f"\n  SCHEMA ERROR  {yaml_file}", fg="red", bold=True)
        for err in report["schema_errors"]:
            click.secho(f"  {err}", fg="red")
        click.echo()

    # Header
    name   = report["display_name"] or report["subclass_id"] or yaml_file
    cls    = report["parent_class"] or "?"
    valid_label = click.style("VALID", fg="green", bold=True) if report["valid"] else click.style("INVALID", fg="red", bold=True)
    click.echo(f"\n  {valid_label}  {name}  [{cls}]")
    click.echo(f"  {'─' * 50}")

    # Features
    cov_colors = {"full": "green", "partial": "yellow", "none": "red"}
    cov_labels = {"full": "FULL   ", "partial": "PARTIAL", "none": "NONE   "}

    for f in report["features"]:
        lvl_tag = f"  L{f['unlock_level']}" if f["unlock_level"] else "     "
        cov = f["coverage"]
        label = click.style(cov_labels[cov], fg=cov_colors[cov])
        click.echo(f"  {label}{lvl_tag}  {f['display_name']}")

        if cov != "full" and f.get("reason"):
            click.echo(f"            → {f['reason']}")

        if "pool_options" in f:
            po = f["pool_options"]
            if po["total"] > 0:
                click.echo(
                    f"            pool: {po['simulatable']}/{po['total']} simulatable"
                )

    # Summary
    s = report["summary"]
    click.echo(f"\n  {'─' * 50}")
    pct = s.get("coverage_pct", 0)
    pct_color = "green" if pct >= 70 else ("yellow" if pct >= 40 else "red")
    click.echo(
        f"  Coverage  {click.style(str(pct) + '%', fg=pct_color, bold=True)}"
        f"  ({s.get('fully_simulated', 0)} full,"
        f" {s.get('partially_simulated', 0)} partial,"
        f" {s.get('not_simulated', 0)} none)"
        f"  across {s.get('total_features', 0)} features\n"
    )

    raise SystemExit(0 if report["valid"] else 1)
