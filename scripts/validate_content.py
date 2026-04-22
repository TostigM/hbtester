"""Batch-validate all YAML content files against their schemas.

Usage:
    python scripts/validate_content.py
    python scripts/validate_content.py --content-dir path/to/content
"""

import argparse
import sys
from pathlib import Path


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

    yaml_files = list(content_dir.rglob("*.yaml"))
    if not yaml_files:
        print(f"No YAML files found in {content_dir}")
        return 0

    print(f"Found {len(yaml_files)} YAML files. Validation not yet implemented (M1).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
