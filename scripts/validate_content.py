"""Batch-validate all YAML content files against their schemas.

Usage:
    python scripts/validate_content.py
    python scripts/validate_content.py --content-dir path/to/content

Content files must have a ``content_type`` field that matches one of the known
types.  Files with unknown content_type are reported as warnings, not errors.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml

from balance_framework.schema.exceptions import ValidationError
from balance_framework.schema.validators import (
    validate_background,
    validate_class,
    validate_feat,
    validate_magic_item,
    validate_monster,
    validate_species,
    validate_spell,
    validate_subclass,
)

_VALIDATORS = {
    "class": validate_class,
    "subclass": validate_subclass,
    "species": validate_species,
    "background": validate_background,
    "spell": validate_spell,
    "magic_item": validate_magic_item,
    "monster": validate_monster,
    "feat": validate_feat,
}


def _validate_file(path: Path) -> list[str]:
    """Return a list of error strings for this file, empty if valid."""
    try:
        data: Any = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return [f"YAML parse error: {exc}"]

    if not isinstance(data, dict):
        return ["File does not contain a YAML mapping at the top level"]

    content_type = data.get("content_type")
    if content_type not in _VALIDATORS:
        return [f"Unknown or missing content_type: {content_type!r}"]

    try:
        _VALIDATORS[content_type](data)
    except ValidationError as exc:
        return [str(exc)]
    return []


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate YAML content files.")
    parser.add_argument(
        "--content-dir",
        type=Path,
        default=Path("content"),
        help="Path to the content directory (default: content/)",
    )
    args = parser.parse_args()

    content_dir: Path = args.content_dir
    if not content_dir.exists():
        print(f"Content directory not found: {content_dir}")
        return 1

    yaml_files = sorted(content_dir.rglob("*.yaml"))
    if not yaml_files:
        print(f"No YAML files found in {content_dir}")
        return 0

    errors: list[tuple[Path, list[str]]] = []
    for path in yaml_files:
        file_errors = _validate_file(path)
        if file_errors:
            errors.append((path, file_errors))

    total = len(yaml_files)
    failed = len(errors)
    passed = total - failed

    print(f"Validated {total} files: {passed} passed, {failed} failed")
    for path, errs in errors:
        print(f"\n  FAIL  {path}")
        for err in errs:
            print(f"        {err}")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
