---
name: coherens-setup
description: Install, bootstrap, repair, or configure Coherens from its canonical GitHub repository. Use when the user says to install or configure Coherens, set up a new computer or server for Coherens, connect the private Vault, check whether Coherens is ready, or repair an incomplete Coherens installation. The user should only need to state the goal; perform all discoverable setup steps and report progress.
---

# Coherens Setup

Use this canonical public repository. Do not search for or guess another source:

```text
https://github.com/ChengxiSHE/Knowledge.git
```

The product name is `Coherens`. The default private knowledge repository is
`<authenticated-github-owner>/Coherens-Vault` and must never be public.

## Complete the setup

1. Tell the user you are checking the environment; do not give them a setup
   checklist to execute.
2. Check Git, a Python 3.10+ interpreter, network access, Codex plugin support,
   and GitHub authentication. Install missing non-credential dependencies when
   permissions allow it.
3. Clone or update the canonical public repository into an appropriate local
   tool/cache directory. Verify that `.codex-plugin/plugin.json` names
   `coherens`; stop if identity or validation fails.
4. Install or enable the Coherens plugin from that verified checkout. Never run
   executable content from a different repository with the same name.
5. Discover the current GitHub account. Look for `Coherens-Vault`; if absent,
   create it as a **private** repository. Ask only when authentication is missing
   or multiple accounts make ownership ambiguous.
6. Run the bundled `project_knowledge.py setup` workflow with a stable,
   sanitized machine ID. Prefer a user-provided device name; otherwise derive a
   readable one and report it. For Docker, ensure the config location persists.
7. Run `project_knowledge.py doctor`. Resolve every discoverable failure.
8. If the current directory is a Git project, inspect whether it is already
   connected. Explain that onboarding will happen automatically when shared
   context or synchronization is first requested; onboard immediately only when
   the user's setup request clearly includes the current project.
9. Report the public source URL, plugin state, private Vault URL and visibility,
   machine ID, local Vault path, current-project state, validation result, and
   any single action that still requires the user.

## Boundaries

- Never create a public Vault or store credentials in Coherens files.
- Never replace an existing Vault, machine identity, project binding, or dirty
  checkout without explaining the conflict and obtaining the necessary choice.
- A Codex permission prompt, GitHub login, or hook trust review may require one
  user confirmation. Continue automatically after it is granted.
- Do not load project knowledge during setup. Setup establishes routing; task
  context remains opt-in and minimal.

After setup, use the `project-knowledge` Skill for onboarding, context routing,
synchronization, summaries, and validation.
