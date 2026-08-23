#!/usr/bin/env python3
"""Install the complete Coherens plugin into the personal Codex marketplace."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


PLUGIN_NAME = "coherens"


def load_json(path: Path) -> dict:
    if not path.exists():
        return {
            "name": "personal",
            "interface": {"displayName": "Personal"},
            "plugins": [],
        }
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("plugins"), list):
        raise ValueError(f"Invalid marketplace file: {path}")
    return data


def copy_plugin(source: Path, target: Path, replace: bool) -> None:
    if source == target:
        return
    if target.exists():
        if not replace:
            raise ValueError(f"Plugin already exists: {target}; rerun with --replace after review")
        shutil.rmtree(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(
        source,
        target,
        ignore=shutil.ignore_patterns(".git", "generated", "__pycache__", ".DS_Store"),
    )


def register_marketplace(path: Path, replace: bool) -> str:
    marketplace = load_json(path)
    marketplace_name = str(marketplace.get("name") or "personal")
    entry = {
        "name": PLUGIN_NAME,
        "source": {"source": "local", "path": f"./plugins/{PLUGIN_NAME}"},
        "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
        "category": "Productivity",
    }
    plugins = marketplace["plugins"]
    matches = [index for index, item in enumerate(plugins) if item.get("name") == PLUGIN_NAME]
    if matches:
        current = plugins[matches[0]]
        if current != entry and not replace:
            raise ValueError(
                f"Marketplace already contains a different {PLUGIN_NAME} entry; use --replace after review"
            )
        plugins[matches[0]] = entry
    else:
        plugins.append(entry)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(marketplace, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    return marketplace_name


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", default=str(Path.home() / "plugins" / PLUGIN_NAME))
    parser.add_argument(
        "--marketplace",
        default=str(Path.home() / ".agents" / "plugins" / "marketplace.json"),
    )
    parser.add_argument("--replace", action="store_true")
    parser.add_argument("--no-enable", action="store_true")
    args = parser.parse_args()

    source = Path(__file__).resolve().parents[1]
    manifest_path = source / ".codex-plugin" / "plugin.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("name") != PLUGIN_NAME:
        print(f"ERROR: unexpected plugin identity in {manifest_path}", file=sys.stderr)
        return 2

    try:
        target = Path(args.target).expanduser().resolve()
        marketplace_path = Path(args.marketplace).expanduser().resolve()
        copy_plugin(source, target, args.replace)
        marketplace_name = register_marketplace(marketplace_path, args.replace)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    enabled = False
    if not args.no_enable:
        codex = shutil.which("codex")
        if not codex:
            print("ERROR: Codex CLI is unavailable; plugin files were installed but not enabled", file=sys.stderr)
            return 2
        result = subprocess.run(
            [codex, "plugin", "add", f"{PLUGIN_NAME}@{marketplace_name}"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if result.returncode != 0:
            print(result.stderr.strip() or result.stdout.strip(), file=sys.stderr)
            return result.returncode
        enabled = True

    print(
        json.dumps(
            {
                "plugin": PLUGIN_NAME,
                "source": str(source),
                "target": str(target),
                "marketplace": str(marketplace_path),
                "marketplace_name": marketplace_name,
                "enabled": enabled,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
