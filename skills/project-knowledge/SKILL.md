---
name: project-knowledge
description: Locate, read, register, synchronize, validate, or summarize a Git-backed multi-workspace project knowledge repository. Use only when the user explicitly invokes this skill for shared project context or knowledge maintenance; ordinary coding tasks should use the local repository and PROGRESS.md without loading shared knowledge.
---

# Project Knowledge

Keep Markdown and Git as the source of truth. Use the bundled deterministic
script for identity, sync cursors, registry updates, summaries, and validation.

Resolve the script from this skill directory as
`scripts/project_knowledge.py`. Never assume the current working directory is
the knowledge repository.

## Route the request

- **Read context:** Run `locate` from the code project. Open the returned project
  `index.md`, select the context pack that matches the task, and follow only its
  links. Compare every `verified_commit` with the local or target commit. Do not
  scan the complete knowledge repository unless the map or validation is broken.
- **Connect a code project:** Run `bootstrap` only after the user identifies the
  project ID, stable workspace ID, version track, local knowledge path, and
  knowledge repository name. Review existing `AGENTS.md` before the script adds
  the progress section.
- **Register a workspace:** Run `register-workspace`. Stable workspace IDs must
  be registered before sync.
- **Sync progress:** Inspect the code and knowledge repository Git states first.
  Update the local knowledge checkout with a fast-forward-only pull only when it
  is clean. Run `sync`, then `validate`. Review generated logs and workspace
  state before committing. Commit only files created or updated by this workflow
  and push only when the user requested cloud synchronization.
- **Daily summary:** Run `daily-summary` for the requested date. Read each linked
  evidence record. Promote only verified, reusable conclusions to common notes,
  runbooks, version notes, or decisions; keep machine-only facts in workspace or
  environment notes. Fill the summary's curated outcome, validate, and then
  commit only the reviewed knowledge changes.
- **Validate:** Run `validate`. Fix broken routes, metadata, duplicate IDs, and
  links in authored Markdown. Registered workspaces without a synchronized state
  are warnings until strict validation is requested.

## Safety and boundaries

- Do not put secrets, tokens, private keys, or full terminal output in Markdown.
- Do not overwrite unrelated dirty Git changes or use destructive Git commands.
- Do not infer that one workspace is current from timestamps alone. Match
  `project_id`, `workspace_id`, `version_track`, and Git commit.
- Do not promote raw progress automatically. A daily summary is evidence routing,
  not proof that a conclusion is durable.
- A machine cannot summarize unsynchronized progress from another offline
  machine. Report that gap explicitly.

Read [references/layout.md](references/layout.md) when adding a new project,
changing metadata, or deciding where knowledge belongs.

