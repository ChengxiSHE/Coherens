#!/usr/bin/env python3
"""Install the bundled skills without overwriting existing installations."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--target",
        default=str(Path.home() / ".agents" / "skills"),
        help="Skill directory used by the target agent",
    )
    parser.add_argument("--replace", action="store_true", help="Replace only these two installed skills")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    source_root = root / "skills"
    target_root = Path(args.target).expanduser().resolve()
    target_root.mkdir(parents=True, exist_ok=True)
    names = ["project-knowledge", "knowledge-graph-view"]
    for name in names:
        source = source_root / name
        target = target_root / name
        if target.exists():
            if not args.replace:
                print(f"ERROR: already installed: {target}", file=sys.stderr)
                return 2
            shutil.rmtree(target)
        shutil.copytree(source, target)
        print(f"Installed {name} to {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

