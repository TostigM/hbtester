"""Flask API for the D&D Homebrew Balance Framework.

Endpoints:
  GET  /api/health           — liveness probe
  GET  /api/baselines        — serve pre-generated metadata.json
  GET  /api/subclasses/<id>  — serve one subclass baseline JSON
  POST /api/simulate         — accept homebrew YAML, run sim, return results
"""

from __future__ import annotations

import json
import os
import sys
import threading
import time
from collections import defaultdict
from pathlib import Path

import yaml
from flask import Flask, jsonify, request
from flask_cors import CORS

# Allow importing balance_framework from src/
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

app = Flask(__name__)
CORS(app)

# ---------------------------------------------------------------------------
# Configuration (override via environment variables)
# ---------------------------------------------------------------------------

CONTENT_DIR   = Path(os.environ.get("CONTENT_DIR",   "content"))
BASELINES_DIR = Path(os.environ.get("BASELINES_DIR", "baselines/v1.3"))
MAX_RUNS      = int(os.environ.get("MAX_RUNS",  "100"))
MAX_LEVEL     = int(os.environ.get("MAX_LEVEL", "10"))

# ---------------------------------------------------------------------------
# Rate limiter (in-memory; resets on dyno restart — acceptable for free tier)
# ---------------------------------------------------------------------------

_rate_data: dict[str, list[float]] = defaultdict(list)
_rate_lock  = threading.Lock()
_RATE_MAX   = 5
_RATE_WIN   = 60  # seconds


def _rate_ok(ip: str) -> bool:
    now = time.monotonic()
    with _rate_lock:
        ts = _rate_data[ip]
        ts[:] = [t for t in ts if now - t < _RATE_WIN]
        if len(ts) >= _RATE_MAX:
            return False
        ts.append(now)
        return True


# ---------------------------------------------------------------------------
# Registry — loaded once at startup, shared across requests (read-only).
# Simulation temporarily injects the homebrew subclass under _sim_lock.
# ---------------------------------------------------------------------------

_registry     = None
_registry_lock = threading.Lock()
_sim_lock      = threading.Lock()   # serialises registry mutations


def _get_registry():
    global _registry
    with _registry_lock:
        if _registry is None:
            from balance_framework.registry.loader import load_content_directory
            from balance_framework.registry.registry import ContentRegistry
            app.logger.info("Loading content registry from %s …", CONTENT_DIR)
            _registry = ContentRegistry(load_content_directory(CONTENT_DIR))
            app.logger.info("Registry loaded.")
    return _registry


# Warm up at import time so the first real request isn't slow.
try:
    _get_registry()
except Exception as exc:  # pragma: no cover
    app.logger.warning("Registry warm-up failed: %s", exc)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "version": "0.1.0"})


@app.route("/api/baselines")
def baselines():
    path = BASELINES_DIR / "metadata.json"
    if not path.exists():
        return jsonify({"error": "Baseline data not found"}), 404
    return jsonify(json.loads(path.read_text(encoding="utf-8")))


@app.route("/api/subclasses/<subclass_id>")
def subclass_data(subclass_id: str):
    if not subclass_id.replace("_", "").isalnum():
        return jsonify({"error": "Invalid subclass ID"}), 400
    path = BASELINES_DIR / "subclasses" / f"{subclass_id}.json"
    if not path.exists():
        return jsonify({"error": f"Subclass '{subclass_id}' not found"}), 404
    return jsonify(json.loads(path.read_text(encoding="utf-8")))


@app.route("/api/simulate", methods=["POST"])
def simulate():
    # Rate limit by IP (Render/Railway set X-Forwarded-For)
    ip = request.headers.get("X-Forwarded-For", request.remote_addr or "").split(",")[0].strip()
    if not _rate_ok(ip):
        return jsonify({"error": "Rate limit exceeded — max 5 requests per minute."}), 429

    body = request.get_json(silent=True)
    if not body or "yaml_content" not in body:
        return jsonify({"error": "JSON body with 'yaml_content' field required."}), 400

    runs  = min(max(int(body.get("runs",  50)), 1), MAX_RUNS)
    level = min(max(int(body.get("level",  5)), 1), MAX_LEVEL)

    # 1. Parse YAML (safe_load only — no arbitrary code execution)
    try:
        parsed = yaml.safe_load(body["yaml_content"])
    except yaml.YAMLError as exc:
        return jsonify({"error": f"YAML parse error: {exc}"}), 400

    if not isinstance(parsed, dict):
        return jsonify({"error": "YAML root must be a mapping."}), 400
    if parsed.get("content_type") != "subclass":
        return jsonify({"error": "content_type must be 'subclass'."}), 400

    # 2. Validate against schema
    try:
        from balance_framework.schema.types import Subclass
        subclass_obj = Subclass(**parsed)
    except Exception as exc:
        return jsonify({"error": f"Schema validation failed: {exc}"}), 400

    # 3. Check that we have a default build for this class
    from balance_framework.cli.test_commands import _CLASS_DEFAULTS
    if subclass_obj.parent_class not in _CLASS_DEFAULTS:
        supported = sorted(_CLASS_DEFAULTS)
        return jsonify({
            "error": (
                f"No default build for class '{subclass_obj.parent_class}'. "
                f"Supported: {supported}"
            )
        }), 400

    # 4. Run simulation (serialised so registry mutations don't race)
    try:
        with _sim_lock:
            result = _run_simulation(subclass_obj, runs, level)
    except Exception as exc:
        app.logger.exception("Simulation error")
        return jsonify({"error": f"Simulation error: {exc}"}), 500

    return jsonify(result)


# ---------------------------------------------------------------------------
# Simulation helper
# ---------------------------------------------------------------------------


def _run_simulation(subclass_obj, runs: int, level: int) -> dict:
    """Inject the homebrew subclass, run the harness, restore registry."""
    from balance_framework.registry.character_builder import CharacterBuild
    from balance_framework.harnesses.subclass import run_subclass_build
    from balance_framework.harnesses.base import STANDARD_ENCOUNTERS, monster_enemy_band
    from balance_framework.cli.test_commands import _CLASS_DEFAULTS

    registry  = _get_registry()
    class_id  = subclass_obj.parent_class
    sc_id     = subclass_obj.id

    # Temporarily inject the homebrew subclass into the shared registry.
    # The _sim_lock ensures no other simulation runs concurrently.
    old = registry._subclasses.get(sc_id)
    registry._subclasses[sc_id] = subclass_obj
    try:
        defaults = _CLASS_DEFAULTS[class_id]
        build    = CharacterBuild(class_id=class_id, subclass_id=sc_id, level=level, **defaults)

        enc_results: dict = {}
        for enc_name, monster_id, count in STANDARD_ENCOUNTERS:
            factory = lambda s, mid=monster_id, cnt=count: monster_enemy_band(mid, cnt, registry)
            enc_results[enc_name] = run_subclass_build(
                build, sc_id, registry, n=runs, base_seed=0, enemy_factory=factory,
            )
    finally:
        # Always restore — even if the simulation raised.
        if old is None:
            registry._subclasses.pop(sc_id, None)
        else:
            registry._subclasses[sc_id] = old

    win_rates   = [r.suite.win_rate("party") for r in enc_results.values()]
    avg_rnd     = [r.suite.avg_rounds        for r in enc_results.values()]

    def _cs_val(r, attr: str) -> float:
        cs = r.combatant_stats.get("variant")
        return getattr(cs, attr, 0.0) if cs else 0.0

    return {
        "subclass_id":  sc_id,
        "class_id":     class_id,
        "display_name": subclass_obj.display_name,
        "level":        level,
        "runs":         runs,
        "aggregate": {
            "avg_win_rate": sum(win_rates) / len(win_rates),
            "min_win_rate": min(win_rates),
            "avg_rounds":   sum(avg_rnd)   / len(avg_rnd),
        },
        "encounters": {
            enc_name: {
                "win_rate":   r.suite.win_rate("party"),
                "avg_rounds": r.suite.avg_rounds,
                "avg_damage": _cs_val(r, "avg_damage_dealt"),
                "avg_kills":  _cs_val(r, "avg_kills"),
                "survival_rate": _cs_val(r, "survival_rate"),
            }
            for enc_name, r in enc_results.items()
        },
    }


# ---------------------------------------------------------------------------
# Entry point (local dev only — production uses gunicorn via Procfile)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
