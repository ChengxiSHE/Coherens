# Knowledge layout and routing

The root `PROJECT_MAP.md` is the human map. `registry.yaml` is the machine
registry. Each `projects/<project-id>/index.md` is the project routing map.
Each project also has a mandatory `PROJECT_PROFILE.md`: the README-quality,
commit-bound explanation produced from a one-time analysis before first sync.

Store knowledge by ownership:

- `common/`: conclusions verified across the relevant workspaces
- `environments/`: operating-system, container, hardware, or runtime differences
- `workspaces/`: current state of a registered machine or container
- `versions/`: main, experiment, private, and open-source track differences
- `runbooks/`: repeatable operations with prerequisites and verification
- `decisions/`: durable choices, alternatives, consequences, and effective commit
- `logs/`: immutable synchronized progress evidence and daily summaries
- `context-packs/`: short task-specific link lists and current constraints

The Project Profile must cover purpose and scope, architecture and execution
flow, directory/module responsibilities, key scripts and interfaces, setup/run/
verification commands, dependencies and environments, constraints, and the
evidence files reviewed. It remains a project-level entry point; do not fragment
its initial explanation across endpoint or version notes.

Knowledge documents require `type`, `id`, `title`, and `status`; project-owned
documents also require `project`. Use `workspace_scope`, `version_scope`, and
`verified_commit` whenever applicability depends on them. Use relative Markdown
links for relationships.

The code repository commits `.kb/project.yaml`. The local-only
`.kb/workspace.local.yaml`, `.kb/sync-state.json`, and `PROGRESS.md` should be
ignored by Git so different hosts cannot overwrite one another's identity or
progress cursor.
