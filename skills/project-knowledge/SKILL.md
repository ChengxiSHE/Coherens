---
name: project-knowledge
description: Operate Coherens, the Git-backed shared project knowledge workflow. Use when the user asks in natural language to set up Coherens, connect or register the current project, synchronize or upload project progress, continue work across machines or agents, read shared project context, create a daily summary, validate the knowledge vault, or inspect project/workspace/version state. Do not trigger for ordinary coding that does not request shared context or synchronization.
---

# Coherens Project Knowledge

Keep Markdown and Git as the source of truth. Use the bundled deterministic
script for identity, sync cursors, registry updates, summaries, and validation.

Resolve the script from this skill directory as
`scripts/project_knowledge.py`. Never assume the current working directory is
the knowledge repository.

## Route the request

- **First machine setup:** Inspect Git and GitHub authentication. Ask only for
  the private Vault repository when it cannot be inferred. If GitHub CLI is
  authenticated, look for `Coherens-Vault` in the current account and create it
  as a private repository when absent. Never create a public Vault. Run `setup`;
  clone or initialize the Vault and verify its registry. This is the only
  required machine-level setup. Run `doctor` afterward and resolve every
  discoverable failure before reporting completion.
- **Natural-language onboarding:** For requests such as "把当前项目接入知识库",
  inspect the current Git repository and run `onboard`. Infer project ID,
  repository, branch/version track, environment, and stable machine ID. Ask only
  when two registered projects are plausible or a value cannot be discovered.
- **Natural-language synchronization:** For requests such as "把项目 A 同步到仓库",
  run `publish`. It performs a clean-Vault preflight, fast-forward pull,
  registration/onboarding when needed, progress synchronization, validation,
  scoped commit, and push. Inspect and report both code and Vault Git states.
- **Read context:** Run `locate` from the code project. Open the returned project
  `index.md`, select the context pack that matches the task, and follow only its
  links. Compare every `verified_commit` with the local or target commit. Do not
  scan the complete knowledge repository unless the map or validation is broken.
- **Connect a code project manually:** Use `bootstrap` only for overrides or
  recovery. Prefer `onboard`, which derives safe defaults and registers both the
  project and current workspace.
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
- **Session reminder:** The bundled `SessionStart` hook may report missing local
  setup or project registration. Treat it as routing context: explain what you
  are checking, then perform the missing steps when relevant to the user's
  request. Never load the Vault merely because the hook ran.

## Safety and boundaries

- Do not put secrets, tokens, private keys, or full terminal output in Markdown.
- Do not overwrite unrelated dirty Git changes or use destructive Git commands.
- Do not infer that one workspace is current from timestamps alone. Match
  `project_id`, `workspace_id`, `version_track`, and Git commit.
- Do not promote raw progress automatically. A daily summary is evidence routing,
  not proof that a conclusion is durable.
- A machine cannot summarize unsynchronized progress from another offline
  machine. Report that gap explicitly.
- Never bypass Git credentials, sandbox permissions, protected branches, merge
  conflicts, or a dirty shared Vault. Stop with one concrete recovery action.
- Do not expose raw hostnames in the Vault. Workspace IDs come from the local
  machine configuration and must be sanitized.

Read [references/layout.md](references/layout.md) when adding a new project,
changing metadata, or deciding where knowledge belongs.
