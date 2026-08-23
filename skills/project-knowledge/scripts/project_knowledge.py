#!/usr/bin/env python3
"""Deterministic project knowledge routing, sync, and summarization."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover - exercised by runtime setup
    raise SystemExit("PyYAML is required. Install it with: python -m pip install PyYAML") from exc


FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*(?:\n|\Z)", re.DOTALL)
MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
REQUIRED_META = {"type", "id", "title", "status"}
PROJECT_META_TYPES = {
    "collection",
    "context-pack",
    "daily-summary",
    "decision",
    "environment",
    "progress-log",
    "project",
    "runbook",
    "version",
    "workspace",
}
EXCLUDED_KNOWLEDGE_PARTS = {
    ".git",
    "generated",
    "skills",
    "templates",
    "tests",
    "tools",
    "__pycache__",
}

AGENTS_SECTION = """## Progress Log

For every non-trivial project task, update `PROGRESS.md` before finishing.

Keep each entry short and include the date, local workspace ID, branch and
commit, what changed and why, verification, unresolved issues, and whether the
result should be promoted to shared knowledge.

Do not record secrets or full terminal output. Do not access or sync the shared
knowledge repository unless the user explicitly invokes the project knowledge
workflow. If `PROGRESS.md` does not exist, create it.
"""

PROGRESS_TEMPLATE = """# Project Progress

## YYYY-MM-DD HH:MM | workspace-id

- Branch: `branch-name`
- Commit: `commit-id`
- Changed: Describe the result and reason.
- Verified: Describe the verification performed.
- Unresolved: None.
- Promote to shared knowledge: no
"""


class KnowledgeError(RuntimeError):
    pass


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise KnowledgeError(f"Required file not found: {path}")
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise KnowledgeError(f"Expected a YAML mapping: {path}")
    return data


def write_yaml(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rendered = yaml.safe_dump(data, sort_keys=False, allow_unicode=True)
    path.write_text(rendered, encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def find_project_root(start: Path) -> Path:
    current = start.resolve()
    for candidate in (current, *current.parents):
        if (candidate / ".kb" / "project.yaml").exists():
            return candidate
    raise KnowledgeError("No .kb/project.yaml found in this directory or its parents")


def resolve_project_root(value: str | None) -> Path:
    return find_project_root(Path(value or os.getcwd()))


def resolve_knowledge_root(
    explicit: str | None, project_root: Path | None = None
) -> Path:
    if explicit:
        return Path(explicit).expanduser().resolve()
    env_path = os.environ.get("PROJECT_KB_ROOT")
    if env_path:
        return Path(env_path).expanduser().resolve()
    if project_root:
        local_path = project_root / ".kb" / "workspace.local.yaml"
        local = load_yaml(local_path)
        configured = local.get("knowledge_root")
        if configured:
            candidate = Path(str(configured)).expanduser()
            if not candidate.is_absolute():
                candidate = project_root / candidate
            return candidate.resolve()
    raise KnowledgeError(
        "Knowledge root is unknown. Pass --knowledge-root, set PROJECT_KB_ROOT, "
        "or configure .kb/workspace.local.yaml"
    )


def git_value(project_root: Path, *args: str, default: str = "unknown") -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=project_root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    value = result.stdout.strip()
    return value if result.returncode == 0 and value else default


def git_state(project_root: Path) -> dict[str, Any]:
    status = git_value(project_root, "status", "--porcelain", default="")
    return {
        "branch": git_value(project_root, "branch", "--show-current"),
        "commit": git_value(project_root, "rev-parse", "HEAD"),
        "dirty": bool(status),
    }


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def frontmatter_and_body(text: str) -> tuple[dict[str, Any], str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, text
    data = yaml.safe_load(match.group(1)) or {}
    if not isinstance(data, dict):
        return {}, text
    return data, text[match.end() :]


def frontmatter_text(meta: dict[str, Any], body: str) -> str:
    yaml_text = yaml.safe_dump(meta, sort_keys=False, allow_unicode=True).strip()
    return f"---\n{yaml_text}\n---\n\n{body.rstrip()}\n"


def add_gitignore_entries(project_root: Path) -> None:
    path = project_root / ".gitignore"
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    entries = ["PROGRESS.md", ".kb/workspace.local.yaml", ".kb/sync-state.json"]
    missing = [entry for entry in entries if entry not in existing.splitlines()]
    if missing:
        prefix = "" if not existing or existing.endswith("\n") else "\n"
        write_text(path, existing + prefix + "\n".join(missing) + "\n")


def command_bootstrap(args: argparse.Namespace) -> None:
    root = Path(args.project_root).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    kb_dir = root / ".kb"
    kb_dir.mkdir(exist_ok=True)

    project_config = kb_dir / "project.yaml"
    if project_config.exists() and not args.force:
        raise KnowledgeError(f"Already configured: {project_config}")
    write_yaml(
        project_config,
        {
            "schema_version": 1,
            "project_id": args.project_id,
            "knowledge_repository": args.knowledge_repository,
        },
    )
    write_yaml(
        kb_dir / "workspace.local.yaml",
        {
            "schema_version": 1,
            "workspace_id": args.workspace_id,
            "version_track": args.version_track,
            "knowledge_root": str(Path(args.knowledge_root).expanduser().resolve()),
        },
    )

    agents_path = root / "AGENTS.md"
    existing_agents = agents_path.read_text(encoding="utf-8") if agents_path.exists() else ""
    if "## Progress Log" not in existing_agents:
        prefix = "" if not existing_agents or existing_agents.endswith("\n") else "\n"
        write_text(agents_path, existing_agents + prefix + "\n" + AGENTS_SECTION)
    progress_path = root / "PROGRESS.md"
    if not progress_path.exists():
        write_text(progress_path, PROGRESS_TEMPLATE)
    add_gitignore_entries(root)
    print(f"Configured project workspace at {root}")


def get_local_identity(project_root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    project = load_yaml(project_root / ".kb" / "project.yaml")
    workspace = load_yaml(project_root / ".kb" / "workspace.local.yaml")
    for key, source, label in (
        ("project_id", project, ".kb/project.yaml"),
        ("workspace_id", workspace, ".kb/workspace.local.yaml"),
        ("version_track", workspace, ".kb/workspace.local.yaml"),
    ):
        if not source.get(key):
            raise KnowledgeError(f"Missing {key} in {label}")
    return project, workspace


def command_locate(args: argparse.Namespace) -> None:
    project_root = resolve_project_root(args.project_root)
    project, workspace = get_local_identity(project_root)
    knowledge_root = resolve_knowledge_root(args.knowledge_root, project_root)
    entry = knowledge_root / "projects" / str(project["project_id"]) / "index.md"
    result = {
        "project_root": str(project_root),
        "knowledge_root": str(knowledge_root),
        "project_id": project["project_id"],
        "workspace_id": workspace["workspace_id"],
        "version_track": workspace["version_track"],
        "knowledge_entry": str(entry),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


def command_register_workspace(args: argparse.Namespace) -> None:
    knowledge_root = resolve_knowledge_root(args.knowledge_root)
    registry_path = knowledge_root / "registry.yaml"
    registry = load_yaml(registry_path)
    projects = registry.setdefault("projects", {})
    if args.project_id not in projects:
        raise KnowledgeError(f"Project is not registered: {args.project_id}")
    workspaces = projects[args.project_id].setdefault("workspaces", {})
    existing = workspaces.get(args.workspace_id)
    requested = {
        "environment": args.environment,
        "role": args.role,
        "status": args.status,
    }
    if existing and existing != requested and not args.force:
        raise KnowledgeError(
            f"Workspace already exists with different values: {args.workspace_id}; "
            "use --force to replace it"
        )
    workspaces[args.workspace_id] = requested
    write_yaml(registry_path, registry)
    print(f"Registered {args.workspace_id} for {args.project_id}")


def validate_registered_identity(
    knowledge_root: Path, project_id: str, workspace_id: str, version_track: str
) -> None:
    registry = load_yaml(knowledge_root / "registry.yaml")
    project = (registry.get("projects") or {}).get(project_id)
    if not project:
        raise KnowledgeError(f"Project is not registered: {project_id}")
    if workspace_id not in (project.get("workspaces") or {}):
        raise KnowledgeError(
            f"Workspace is not registered: {workspace_id}. Register it before syncing."
        )
    tracks = project.get("version_tracks") or []
    if version_track not in tracks:
        raise KnowledgeError(
            f"Version track {version_track!r} is not registered for {project_id}"
        )


def read_sync_delta(progress_path: Path, state_path: Path) -> tuple[str, bool, dict[str, Any]]:
    content = progress_path.read_bytes()
    state: dict[str, Any] = {}
    if state_path.exists():
        try:
            state = json.loads(state_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            state = {}
    offset = int(state.get("progress_offset", 0))
    prefix_hash = state.get("progress_prefix_sha256", "")
    current_prefix_hash = hashlib.sha256(content[:offset]).hexdigest()
    appended = offset <= len(content) and (offset == 0 or prefix_hash == current_prefix_hash)
    delta = content[offset:] if appended else content
    new_state = {
        "progress_offset": len(content),
        "progress_prefix_sha256": hashlib.sha256(content).hexdigest(),
    }
    return delta.decode("utf-8"), not appended, new_state


def command_sync(args: argparse.Namespace) -> None:
    project_root = resolve_project_root(args.project_root)
    project, workspace = get_local_identity(project_root)
    knowledge_root = resolve_knowledge_root(args.knowledge_root, project_root)
    project_id = str(project["project_id"])
    workspace_id = str(workspace["workspace_id"])
    version_track = str(workspace["version_track"])
    validate_registered_identity(knowledge_root, project_id, workspace_id, version_track)

    progress_path = project_root / "PROGRESS.md"
    if not progress_path.exists():
        raise KnowledgeError(f"Progress file not found: {progress_path}")
    state_path = project_root / ".kb" / "sync-state.json"
    delta, resync, new_state = read_sync_delta(progress_path, state_path)
    git = git_state(project_root)
    timestamp = now_utc()
    project_dir = knowledge_root / "projects" / project_id
    if not project_dir.exists():
        raise KnowledgeError(f"Knowledge project directory not found: {project_dir}")

    log_link = None
    if delta.strip():
        stamp = timestamp.strftime("%Y-%m-%dT%H%M%SZ")
        log_path = project_dir / "logs" / f"{stamp}__{workspace_id}.md"
        sequence = 2
        while log_path.exists():
            log_path = project_dir / "logs" / f"{stamp}__{workspace_id}__{sequence}.md"
            sequence += 1
        log_id = f"{project_id}-{log_path.stem.replace('__', '-')}"
        meta = {
            "type": "progress-log",
            "id": log_id,
            "title": f"{workspace_id} progress {stamp}",
            "project": project_id,
            "workspace_scope": [workspace_id],
            "version_scope": [version_track],
            "branch": git["branch"],
            "commit": git["commit"],
            "dirty": git["dirty"],
            "resync": resync,
            "synced_at": timestamp.isoformat(),
            "status": "active",
        }
        note = (
            f"# Progress from {workspace_id}\n\n"
            f"Source project: `{project_root}`\n\n"
            f"## Uploaded progress\n\n{delta.strip()}\n"
        )
        write_text(log_path, frontmatter_text(meta, note))
        log_link = f"../logs/{log_path.name}"

    workspace_path = project_dir / "workspaces" / f"{workspace_id}.md"
    workspace_meta = {
        "type": "workspace",
        "id": f"{project_id}-{workspace_id}",
        "title": f"{project_id} workspace {workspace_id}",
        "project": project_id,
        "workspace_scope": [workspace_id],
        "version_scope": [version_track],
        "verified_commit": git["commit"],
        "status": "active",
        "updated_at": timestamp.isoformat(),
    }
    latest = f"[Latest progress log]({log_link})" if log_link else "No new progress log"
    workspace_body = f"""# {workspace_id}

- Version track: `{version_track}`
- Branch: `{git['branch']}`
- Commit: `{git['commit']}`
- Working tree dirty: `{str(git['dirty']).lower()}`
- Last synchronized: `{timestamp.isoformat()}`
- {latest}
"""
    write_text(workspace_path, frontmatter_text(workspace_meta, workspace_body))
    new_state.update(
        {
            "last_synced_at": timestamp.isoformat(),
            "last_commit": git["commit"],
            "last_log": str(log_link or ""),
        }
    )
    write_text(state_path, json.dumps(new_state, ensure_ascii=False, indent=2) + "\n")
    if log_link:
        suffix = " (full resync)" if resync else ""
        print(f"Uploaded new progress for {project_id}/{workspace_id}{suffix}")
    else:
        print(f"No new progress; refreshed {project_id}/{workspace_id} state")


def command_daily_summary(args: argparse.Namespace) -> None:
    knowledge_root = resolve_knowledge_root(args.knowledge_root)
    target_date = args.date or datetime.now().date().isoformat()
    registry = load_yaml(knowledge_root / "registry.yaml")
    project_ids = [args.project_id] if args.project_id else list((registry.get("projects") or {}).keys())
    produced = 0
    for project_id in project_ids:
        logs_dir = knowledge_root / "projects" / project_id / "logs"
        if not logs_dir.exists():
            continue
        records: list[tuple[Path, dict[str, Any], str]] = []
        for path in sorted(logs_dir.glob(f"{target_date}T*.md")):
            meta, body = frontmatter_and_body(path.read_text(encoding="utf-8"))
            if meta.get("type") == "progress-log":
                records.append((path, meta, body))
        if not records:
            continue
        grouped: dict[str, list[tuple[Path, dict[str, Any], str]]] = defaultdict(list)
        candidates: list[Path] = []
        for record in records:
            workspace_scope = record[1].get("workspace_scope") or ["unknown"]
            grouped[str(workspace_scope[0])].append(record)
            if re.search(
                r"(?:promote to shared knowledge\s*:\s*yes|知识候选\s*[:：]\s*是)",
                record[2],
                re.IGNORECASE,
            ):
                candidates.append(record[0])
        body_parts = [f"# {project_id} daily summary for {target_date}", "", "## Evidence by workspace", ""]
        for workspace_id, items in sorted(grouped.items()):
            body_parts.append(f"### {workspace_id}")
            body_parts.append("")
            for path, meta, _ in items:
                body_parts.append(
                    f"- [{path.stem}](../{path.name}) on branch `{meta.get('branch', 'unknown')}` "
                    f"at commit `{meta.get('commit', 'unknown')}`"
                )
            body_parts.append("")
        body_parts.extend(["## Promotion candidates", ""])
        if candidates:
            for path in candidates:
                body_parts.append(f"- [ ] Review [{path.stem}](../{path.name})")
        else:
            body_parts.append("No progress entry explicitly requested promotion.")
        body_parts.extend(
            [
                "",
                "## Curated outcome",
                "",
                "Fill this section after reviewing evidence. Link every promoted conclusion to its owning common note, runbook, version note, or decision.",
            ]
        )
        meta = {
            "type": "daily-summary",
            "id": f"{project_id}-daily-{target_date}",
            "title": f"{project_id} daily summary {target_date}",
            "project": project_id,
            "date": target_date,
            "status": "draft",
        }
        output = logs_dir / "daily" / f"{target_date}.md"
        write_text(output, frontmatter_text(meta, "\n".join(body_parts)))
        produced += 1
        print(f"Wrote {output}")
    if not produced:
        print(f"No progress logs found for {target_date}")


def normalized_link_target(raw: str) -> str | None:
    target = raw.strip().split(maxsplit=1)[0].strip("<>")
    target = target.split("#", 1)[0]
    if not target or target.startswith(("http://", "https://", "mailto:", "obsidian:")):
        return None
    return target


def command_validate(args: argparse.Namespace) -> None:
    knowledge_root = resolve_knowledge_root(args.knowledge_root)
    registry = load_yaml(knowledge_root / "registry.yaml")
    errors: list[str] = []
    warnings: list[str] = []
    ids: dict[str, Path] = {}
    markdown_paths = [
        path
        for path in knowledge_root.rglob("*.md")
        if not EXCLUDED_KNOWLEDGE_PARTS.intersection(path.relative_to(knowledge_root).parts)
        and path.name != "README.md"
    ]
    for path in sorted(markdown_paths):
        text = path.read_text(encoding="utf-8")
        meta, _ = frontmatter_and_body(text)
        relative = path.relative_to(knowledge_root)
        missing = sorted(REQUIRED_META - set(meta))
        if missing:
            errors.append(f"{relative}: missing frontmatter fields {', '.join(missing)}")
        if meta.get("type") in PROJECT_META_TYPES and not meta.get("project") and meta.get("type") != "map":
            errors.append(f"{relative}: project field is required for {meta.get('type')}")
        doc_id = meta.get("id")
        if doc_id:
            if str(doc_id) in ids:
                errors.append(f"{relative}: duplicate id {doc_id!r}, first used by {ids[str(doc_id)].relative_to(knowledge_root)}")
            else:
                ids[str(doc_id)] = path
        for raw in MARKDOWN_LINK_RE.findall(text):
            target = normalized_link_target(raw)
            if target is None:
                continue
            resolved = (path.parent / target).resolve()
            if resolved.suffix == "":
                md_candidate = resolved.with_suffix(".md")
                if md_candidate.exists():
                    resolved = md_candidate
            if not resolved.exists():
                errors.append(f"{relative}: broken link {raw!r}")
    for project_id, project in (registry.get("projects") or {}).items():
        entry = knowledge_root / str(project.get("knowledge_entry", ""))
        if not entry.exists():
            errors.append(f"registry.yaml: {project_id} knowledge_entry does not exist")
        project_dir = knowledge_root / "projects" / str(project_id)
        for workspace_id in (project.get("workspaces") or {}):
            state = project_dir / "workspaces" / f"{workspace_id}.md"
            if not state.exists():
                warnings.append(f"{project_id}: registered workspace has no synchronized state: {workspace_id}")
    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        raise KnowledgeError(f"Validation failed with {len(errors)} error(s)")
    if args.strict and warnings:
        raise KnowledgeError(f"Strict validation failed with {len(warnings)} warning(s)")
    print(f"Validated {len(markdown_paths)} Markdown files with {len(warnings)} warning(s)")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    bootstrap = sub.add_parser("bootstrap", help="Connect a code project to the knowledge repository")
    bootstrap.add_argument("--project-root", required=True)
    bootstrap.add_argument("--project-id", required=True)
    bootstrap.add_argument("--workspace-id", required=True)
    bootstrap.add_argument("--version-track", default="main")
    bootstrap.add_argument("--knowledge-root", required=True)
    bootstrap.add_argument("--knowledge-repository", required=True)
    bootstrap.add_argument("--force", action="store_true")
    bootstrap.set_defaults(func=command_bootstrap)

    locate = sub.add_parser("locate", help="Resolve the current project and knowledge entry")
    locate.add_argument("--project-root")
    locate.add_argument("--knowledge-root")
    locate.set_defaults(func=command_locate)

    register = sub.add_parser("register-workspace", help="Register a stable workspace ID")
    register.add_argument("--knowledge-root", required=True)
    register.add_argument("--project-id", required=True)
    register.add_argument("--workspace-id", required=True)
    register.add_argument("--environment", required=True)
    register.add_argument("--role", required=True)
    register.add_argument("--status", default="active")
    register.add_argument("--force", action="store_true")
    register.set_defaults(func=command_register_workspace)

    sync = sub.add_parser("sync", help="Upload new local progress and refresh workspace state")
    sync.add_argument("--project-root")
    sync.add_argument("--knowledge-root")
    sync.set_defaults(func=command_sync)

    daily = sub.add_parser("daily-summary", help="Build per-project summaries from a day of progress logs")
    daily.add_argument("--knowledge-root", required=True)
    daily.add_argument("--date")
    daily.add_argument("--project-id")
    daily.set_defaults(func=command_daily_summary)

    validate = sub.add_parser("validate", help="Validate metadata, links, and registry routes")
    validate.add_argument("--knowledge-root", required=True)
    validate.add_argument("--strict", action="store_true")
    validate.set_defaults(func=command_validate)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except KnowledgeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
