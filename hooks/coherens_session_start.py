#!/usr/bin/env python3
"""Return only the Coherens onboarding reminder relevant to this session."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path


def config_path() -> Path:
    explicit = os.environ.get("COHERENS_CONFIG")
    if explicit:
        return Path(explicit).expanduser()
    if os.name == "nt":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
        return base / "Coherens" / "config.yaml"
    base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return base / "coherens" / "config.yaml"


def git_root() -> Path | None:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if result.returncode != 0 or not result.stdout.strip():
        return None
    return Path(result.stdout.strip())


def main() -> int:
    context = ""
    if not config_path().exists():
        context = (
            "Coherens is installed but this machine is not configured. On the first relevant "
            "request, proactively explain that you are initializing Coherens, then inspect Git "
            "and GitHub authentication. The canonical public source is "
            "https://github.com/ChengxiSHE/Coherens.git. Ask the user to create an empty Private "
            "Coherens-Vault and provide its clone URL, then verify privacy, register a stable "
            "machine ID, run Coherens setup and doctor, and report machine, Vault, project, and "
            "sync readiness separately. Do not attempt to create the GitHub repository."
        )
    else:
        root = git_root()
        if root and not (root / ".kb" / "project.yaml").exists():
            context = (
                "Coherens is configured on this machine, but the current Git repository is not "
                "registered. When the user requests cross-machine work, shared context, or sync, "
                "proactively run Coherens onboarding before the requested work. Before its first "
                "sync, analyze the existing repository and complete the README-quality Project "
                "Profile, then report the project, workspace, version track, generated files, and "
                "validation result."
            )
    if context:
        print(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "SessionStart",
                        "additionalContext": context,
                    }
                }
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
