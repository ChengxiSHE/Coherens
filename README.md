# Multi-host project knowledge starter

This repository implements a Git-backed Markdown knowledge base for projects
that move between Windows, macOS, and Docker or server workspaces. VS Code is
enough for editing. The browser graph is a generated view, not a source of truth.

## What is authoritative

1. `PROJECT_MAP.md` is the human project map.
2. `registry.yaml` registers stable project, workspace, and version identities.
3. `projects/<project-id>/index.md` routes tasks to a small context pack.
4. Git commits bind knowledge to concrete code revisions.

## Requirements

- Python 3.10 or newer
- PyYAML 6.x
- Git for synchronization with GitHub

Install the Python dependency with `python -m pip install -r requirements.txt`.

## Install the explicit-only skills

Run:

```text
python tools/install_skills.py
```

This installs `$project-knowledge` and `$knowledge-graph-view` under
`~/.agents/skills`. Existing installations are not overwritten. Restart Codex
if the skills do not appear immediately.

## Customize the starter

Replace the example `project-a` values in `PROJECT_MAP.md`, `registry.yaml`, and
`projects/project-a/`. Add one registered workspace ID for every physical or
logical workspace that can upload progress.

## Connect a code project

Invoke `$project-knowledge` and ask it to bootstrap the code repository with:

- project ID
- stable workspace ID
- version track
- absolute local path of this knowledge repository
- GitHub repository name for the knowledge repository

The bootstrap creates or updates:

```text
AGENTS.md                  committed project rule
.kb/project.yaml           committed project identity
.kb/workspace.local.yaml   ignored machine identity and local path
PROGRESS.md                ignored local progress journal
.kb/sync-state.json        ignored incremental upload cursor
```

## Daily operation

- Ordinary coding: Codex updates local `PROGRESS.md` and does not read the shared
  knowledge repository.
- Cross-host work: invoke `$project-knowledge` to read the relevant context pack.
- Upload progress: invoke `$project-knowledge` to sync, validate, commit, and push
  reviewed knowledge changes.
- End of day: sync every active workspace, then invoke the daily summary workflow.
- Visual inspection: invoke `$knowledge-graph-view`; open
  `generated/knowledge-graph.html` in a browser.

## Direct verification

```text
python skills/project-knowledge/scripts/project_knowledge.py validate --knowledge-root .
python skills/knowledge-graph-view/scripts/knowledge_graph.py --knowledge-root .
python -m unittest discover -s tests -v
```

Do not commit passwords, tokens, private keys, or raw command dumps. A central
summary cannot include work that remains unsynchronized on an offline machine.

